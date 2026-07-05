from __future__ import annotations

from typing import Optional

from backend.curriculum.curriculum import Curriculum

from .models import ASSESS_MODE, TEACH_MODE, LearningState, utc_now
from .state_store import FileStateStore


class StateManager:
    def __init__(self, store: FileStateStore, curriculum: Curriculum) -> None:
        self._store = store
        self._curriculum = curriculum

    def load(self, student_id: str) -> LearningState:
        state = self._store.load(student_id)
        if state is None:
            return self.initial_state(student_id)
        self.validate(state)
        return state

    def save(self, state: LearningState) -> None:
        self.validate(state)
        state.updated_at = utc_now()
        self._store.save(state)

    def reset(
        self,
        student_id: str,
        phase: Optional[str] = None,
        lesson: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> LearningState:
        state = self.initial_state(student_id, phase=phase, lesson=lesson, topic=topic)
        self.save(state)
        return state

    def initial_state(
        self,
        student_id: str,
        phase: Optional[str] = None,
        lesson: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> LearningState:
        default_lesson = self._curriculum.default_lesson()
        lesson_id = lesson or default_lesson.lesson_id
        phase_id = phase or default_lesson.phase_id
        topic_name = topic or self._curriculum.first_topic(lesson_id)
        state = LearningState(
            student_id=student_id,
            current_phase=phase_id,
            current_lesson=lesson_id,
            current_topic=topic_name,
        )
        self.validate(state)
        return state

    def validate(self, state: LearningState) -> None:
        if state.current_mode not in {TEACH_MODE, ASSESS_MODE}:
            raise ValueError(f"Invalid current_mode: {state.current_mode}")
        self._curriculum.lesson(state.current_lesson)
        self._curriculum.topic(state.current_lesson, state.current_topic)
