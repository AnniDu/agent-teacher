from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


YamlMap = dict[str, Any]


@dataclass(frozen=True)
class NavigationLocation:
    phase: str
    lesson: str
    topic: str | None


@dataclass(frozen=True)
class CurriculumContext:
    course_index: str
    phase_index: str
    lesson: str
    phase_id: str
    lesson_id: str
    previous_lesson_id: str | None
    lesson_path: Path


@dataclass(frozen=True)
class StateContext:
    navigation: YamlMap
    progress: YamlMap
    review_queue: YamlMap
    lesson_note: str | None
    previous_lesson_note: str | None
    lesson_note_path: Path


@dataclass(frozen=True)
class LearningContext:
    curriculum: CurriculumContext
    state: StateContext
