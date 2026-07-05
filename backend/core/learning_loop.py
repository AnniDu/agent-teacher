from __future__ import annotations

from dataclasses import dataclass

from backend.config import Settings
from backend.curriculum.curriculum import Curriculum
from backend.events.event_log import EventLog
from backend.services.assessment_service import AssessmentService
from backend.services.teaching_service import TeachingService, TeachingToolError
from backend.state.models import ASSESS_MODE, TEACH_MODE, LearningState, StateTransition

from .transitions import apply_assessment_transition, transition_to_assess


@dataclass(frozen=True)
class LearningLoopResult:
    message: str
    state: LearningState
    transition: StateTransition


class LearningLoop:
    def __init__(
        self,
        curriculum: Curriculum,
        teaching_service: TeachingService,
        assessment_service: AssessmentService,
        event_log: EventLog,
        settings: Settings,
    ) -> None:
        self._curriculum = curriculum
        self._teaching_service = teaching_service
        self._assessment_service = assessment_service
        self._event_log = event_log
        self._settings = settings

    def run(self, state: LearningState, student_message: str) -> LearningLoopResult:
        self._event_log.append(
            state.student_id,
            "student_message",
            {"message": student_message, "mode": state.current_mode},
        )
        if state.current_mode == TEACH_MODE:
            result = self._teach(state)
        elif state.current_mode == ASSESS_MODE:
            result = self._assess(state, student_message)
        else:
            raise ValueError(f"Invalid current_mode: {state.current_mode}")

        self._event_log.append(
            state.student_id,
            "state_transition",
            {
                "from_mode": result.transition.from_mode,
                "to_mode": result.transition.to_mode,
                "from_topic": result.transition.from_topic,
                "to_topic": result.transition.to_topic,
                "next_step": result.transition.next_step,
            },
        )
        self._event_log.append(
            state.student_id,
            "assistant_message",
            {"message": result.message, "mode": state.current_mode},
        )
        return result

    def _teach(self, state: LearningState) -> LearningLoopResult:
        lesson = self._curriculum.lesson(state.current_lesson)
        topic = self._curriculum.topic(state.current_lesson, state.current_topic)
        try:
            teaching = self._teaching_service.teach(state, self._curriculum, lesson, topic)
        except TeachingToolError as exc:
            self._event_log.append(state.student_id, "tool_call", exc.tool_call_event)
            raise
        if teaching.tool_call_event is not None:
            self._event_log.append(state.student_id, "tool_call", teaching.tool_call_event)
        transition = transition_to_assess(state, teaching.question)
        return LearningLoopResult(message=teaching.message, state=state, transition=transition)

    def _assess(self, state: LearningState, student_message: str) -> LearningLoopResult:
        lesson = self._curriculum.lesson(state.current_lesson)
        topic = self._curriculum.topic(state.current_lesson, state.current_topic)
        assessment = self._assessment_service.assess(state, lesson, topic, student_message)
        self._event_log.append(
            state.student_id,
            "assessment_result",
            {
                "score": assessment.score,
                "feedback": assessment.feedback,
                "misconceptions": assessment.misconceptions,
            },
        )
        transition = apply_assessment_transition(
            state,
            assessment,
            self._curriculum,
            self._settings.assessment_pass_threshold,
        )
        return LearningLoopResult(message=assessment.feedback, state=state, transition=transition)
