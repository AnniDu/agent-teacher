from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from backend.state.models import LearningState


class ChatRequest(BaseModel):
    student_id: str
    message: str


class StateSummary(BaseModel):
    student_id: str
    current_phase: str
    current_lesson: str
    current_topic: str
    current_mode: str
    last_question: Optional[str]
    understanding_score: Optional[float]
    misconceptions: List[str]
    completed_topics: List[str]
    next_step: str
    turn_count: int
    updated_at: str

    @classmethod
    def from_state(cls, state: LearningState) -> "StateSummary":
        return cls(**state.to_dict())


class ChatResponse(BaseModel):
    message: str
    state: StateSummary


class ResetStateRequest(BaseModel):
    phase: Optional[str] = None
    lesson: Optional[str] = None
    topic: Optional[str] = None


class ResetStateResponse(BaseModel):
    ok: bool
    state: StateSummary
