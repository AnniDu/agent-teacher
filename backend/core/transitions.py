from __future__ import annotations

from backend.curriculum.curriculum import Curriculum
from backend.services.assessment_service import AssessmentResult
from backend.state.models import ASSESS_MODE, TEACH_MODE, LearningState, StateTransition


def transition_to_assess(state: LearningState, question: str) -> StateTransition:
    previous_mode = state.current_mode
    previous_topic = state.current_topic
    state.current_mode = ASSESS_MODE
    state.last_question = question
    state.next_step = "wait_for_answer"
    state.turn_count += 1
    return StateTransition(
        from_mode=previous_mode,
        to_mode=state.current_mode,
        from_topic=previous_topic,
        to_topic=state.current_topic,
        next_step=state.next_step,
    )


def apply_assessment_transition(
    state: LearningState,
    assessment: AssessmentResult,
    curriculum: Curriculum,
    pass_threshold: float,
) -> StateTransition:
    previous_mode = state.current_mode
    previous_topic = state.current_topic
    state.understanding_score = assessment.score
    state.misconceptions = assessment.misconceptions
    state.current_mode = TEACH_MODE
    state.turn_count += 1

    if assessment.score >= pass_threshold:
        if state.current_topic not in state.completed_topics:
            state.completed_topics.append(state.current_topic)
        state.last_question = None
        next_topic = curriculum.next_topic(state.current_lesson, state.current_topic)
        if next_topic is None:
            state.next_step = "lesson_complete"
        else:
            state.current_topic = next_topic
            state.next_step = "teach_next_topic"
    else:
        state.next_step = "reteach_current_topic"

    return StateTransition(
        from_mode=previous_mode,
        to_mode=state.current_mode,
        from_topic=previous_topic,
        to_topic=state.current_topic,
        next_step=state.next_step,
    )
