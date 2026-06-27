from __future__ import annotations

import re
from pathlib import Path

from .models import CurriculumContext, NavigationLocation


class CurriculumLoadError(RuntimeError):
    pass


_LINK_RE = re.compile(r"^\d+\.\s+\[(?P<title>.+?)\]\((?P<path>[^)]+)\)", re.MULTILINE)


class CurriculumLoader:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.curriculum_dir = repo_root / "curriculum"

    def load_for_location(self, location: NavigationLocation) -> CurriculumContext:
        phase_number = _phase_number(location.phase)
        course_index_path = self.curriculum_dir / "index.md"
        phase_dir = self.curriculum_dir / f"phase{phase_number}"
        phase_index_path = phase_dir / "index.md"

        course_index = _read_text(course_index_path)
        phase_index = _read_text(phase_index_path)
        lesson_rel_path = self._resolve_lesson_path(location.lesson, phase_index)
        lesson_path = phase_dir / lesson_rel_path
        lesson = _read_text(lesson_path)
        previous_lesson_id = _front_matter_value(lesson, "previous")

        return CurriculumContext(
            course_index=course_index,
            phase_index=phase_index,
            lesson=lesson,
            phase_id=location.phase,
            lesson_id=location.lesson,
            previous_lesson_id=previous_lesson_id,
            lesson_path=lesson_path,
        )

    def _resolve_lesson_path(self, lesson_id: str, phase_index: str) -> Path:
        lesson_paths = [Path(match.group("path")) for match in _LINK_RE.finditer(phase_index)]
        if not lesson_paths:
            raise CurriculumLoadError("Current phase index does not contain lesson links")

        target_prefix = _filename_prefix_for_lesson_id(lesson_id)
        for lesson_path in lesson_paths:
            if lesson_path.name.startswith(target_prefix):
                return lesson_path
        raise CurriculumLoadError(f"Could not resolve lesson {lesson_id} from current phase index")


def _filename_prefix_for_lesson_id(lesson_id: str) -> str:
    match = re.fullmatch(r"P\d+L(\d+)", lesson_id)
    if match:
        return f"lesson{int(match.group(1)):02d}-"

    match = re.fullmatch(r"P\d+LAB(\d+)", lesson_id)
    if match:
        return f"lab{int(match.group(1)):02d}-"

    if re.fullmatch(r"P\d+FINAL", lesson_id):
        return "final-project-"

    raise CurriculumLoadError(f"Invalid lesson id: {lesson_id}")


def _phase_number(phase_id: str) -> int:
    if not phase_id.startswith("P") or not phase_id[1:].isdigit():
        raise CurriculumLoadError(f"Invalid phase id: {phase_id}")
    return int(phase_id[1:])


def _read_text(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError as exc:
        raise CurriculumLoadError(f"Missing curriculum file: {path}") from exc


def _front_matter_value(markdown: str, key: str) -> str | None:
    lines = markdown.splitlines()
    if not lines or lines[0] != "---":
        return None
    for line in lines[1:]:
        if line == "---":
            return None
        prefix = f"{key}:"
        if line.startswith(prefix):
            value = line.removeprefix(prefix).strip().strip('"').strip("'")
            return None if value == "null" else value
    return None
