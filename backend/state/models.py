from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


TEACH_MODE = "teach"
ASSESS_MODE = "assess"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class LearningState:
    student_id: str
    current_phase: str
    current_lesson: str
    current_topic: str
    current_mode: str = TEACH_MODE
    last_question: Optional[str] = None
    understanding_score: Optional[float] = None
    misconceptions: List[str] = field(default_factory=list)
    completed_topics: List[str] = field(default_factory=list)
    next_step: str = "teach_current_topic"
    turn_count: int = 0
    updated_at: str = field(default_factory=utc_now)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningState":
        return cls(
            student_id=str(data["student_id"]),
            current_phase=str(data["current_phase"]),
            current_lesson=str(data["current_lesson"]),
            current_topic=str(data["current_topic"]),
            current_mode=str(data.get("current_mode", TEACH_MODE)),
            last_question=data.get("last_question"),
            understanding_score=data.get("understanding_score"),
            misconceptions=list(data.get("misconceptions", [])),
            completed_topics=list(data.get("completed_topics", [])),
            next_step=str(data.get("next_step", "teach_current_topic")),
            turn_count=int(data.get("turn_count", 0)),
            updated_at=str(data.get("updated_at", utc_now())),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StateTransition:
    from_mode: str
    to_mode: str
    from_topic: str
    to_topic: str
    next_step: str
