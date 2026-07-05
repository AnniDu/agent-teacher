from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from backend.curriculum.curriculum import Curriculum, Lesson, Topic
from backend.state.models import LearningState


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    name: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class ToolContext:
    state: LearningState
    curriculum: Curriculum
    lesson: Lesson
    topic: Topic


ToolFunction = Callable[[ToolCall, ToolContext], ToolResult]
