from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import NavigationLocation, StateContext, YamlMap


class StateLoadError(RuntimeError):
    pass


def load_yaml(path: Path) -> YamlMap:
    try:
        data = yaml.safe_load(path.read_text())
    except FileNotFoundError as exc:
        raise StateLoadError(f"Missing state file: {path}") from exc
    except yaml.YAMLError as exc:
        raise StateLoadError(f"Invalid YAML in {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise StateLoadError(f"Expected mapping in {path}")
    return data


def write_yaml(path: Path, data: YamlMap) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


class StateLoader:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.state_dir = repo_root / "state"

    def load_navigation(self) -> YamlMap:
        return load_yaml(self.state_dir / "navigation.yaml")

    def current_location(self, navigation: YamlMap) -> NavigationLocation:
        current = navigation.get("current")
        if not isinstance(current, dict):
            raise StateLoadError("state/navigation.yaml is missing current")
        phase = current.get("phase")
        lesson = current.get("lesson")
        topic = current.get("topic")
        if not isinstance(phase, str) or not isinstance(lesson, str):
            raise StateLoadError("state/navigation.yaml current.phase and current.lesson must be set")
        if topic is not None and not isinstance(topic, str):
            raise StateLoadError("state/navigation.yaml current.topic must be a string or null")
        return NavigationLocation(phase=phase, lesson=lesson, topic=topic)

    def load_for_location(
        self, location: NavigationLocation, previous_lesson_id: str | None = None
    ) -> StateContext:
        phase_number = _phase_number(location.phase)
        progress_path = self.state_dir / "progress" / f"phase{phase_number}.yaml"
        note_path = self.state_dir / "lesson_notes" / f"{location.lesson}.md"
        lesson_note = note_path.read_text() if note_path.exists() else None
        previous_lesson_note = self.load_lesson_note(previous_lesson_id)
        return StateContext(
            navigation=self.load_navigation(),
            progress=load_yaml(progress_path),
            review_queue=load_yaml(self.state_dir / "review_queue.yaml"),
            lesson_note=lesson_note,
            previous_lesson_note=previous_lesson_note,
            lesson_note_path=note_path,
        )

    def load_lesson_note(self, lesson_id: str | None) -> str | None:
        if not lesson_id:
            return None
        path = self.state_dir / "lesson_notes" / f"{lesson_id}.md"
        return path.read_text() if path.exists() else None


def _phase_number(phase_id: str) -> int:
    if not phase_id.startswith("P") or not phase_id[1:].isdigit():
        raise StateLoadError(f"Invalid phase id: {phase_id}")
    return int(phase_id[1:])
