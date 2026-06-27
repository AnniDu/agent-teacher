from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import LearningContext, YamlMap
from .state_loader import load_yaml, write_yaml


class StateUpdateError(RuntimeError):
    pass


class StateUpdater:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.state_dir = repo_root / "state"

    def apply(self, raw_update: str, context: LearningContext) -> None:
        update = parse_state_update(raw_update)
        state_update = update.get("state_update")
        if not isinstance(state_update, dict):
            raise StateUpdateError("State update must contain a state_update object")

        self._apply_navigation(state_update.get("navigation"))
        self._apply_progress(state_update.get("progress"), context)
        self._apply_review_queue(state_update.get("review_queue"))
        self._apply_lesson_note(state_update.get("lesson_note"), context)

    def _apply_navigation(self, update: Any) -> None:
        if update is None:
            return
        if not isinstance(update, dict):
            raise StateUpdateError("navigation update must be an object")
        path = self.state_dir / "navigation.yaml"
        current = load_yaml(path)
        for section in ("current", "last_completed"):
            section_update = update.get(section)
            if section_update is None:
                continue
            if not isinstance(section_update, dict):
                raise StateUpdateError(f"navigation.{section} must be an object")
            target = current.setdefault(section, {})
            if not isinstance(target, dict):
                raise StateUpdateError(f"navigation.{section} in state must be an object")
            for key in ("phase", "lesson", "topic"):
                if key in section_update:
                    target[key] = section_update[key]
        write_yaml(path, current)

    def _apply_progress(self, update: Any, context: LearningContext) -> None:
        if update is None:
            return
        if not isinstance(update, dict):
            raise StateUpdateError("progress update must be an object")
        phase = update.get("phase") or context.curriculum.phase_id
        if phase != context.curriculum.phase_id:
            raise StateUpdateError("progress update phase must match current phase")
        phase_number = _phase_number(phase)
        path = self.state_dir / "progress" / f"phase{phase_number}.yaml"
        current = load_yaml(path)

        for key in ("status", "score"):
            if key in update:
                current[key] = update[key]

        lesson_id = update.get("lesson_id", context.curriculum.lesson_id)
        if lesson_id != context.curriculum.lesson_id:
            raise StateUpdateError("progress update lesson_id must match current lesson")

        lessons = current.setdefault("lessons", [])
        if not isinstance(lessons, list):
            raise StateUpdateError("progress lessons must be a list")
        lesson_entry = _find_or_create_lesson_entry(lessons, lesson_id)
        for key in ("status", "score", "weak_topics", "completed_topics"):
            if key in update:
                lesson_entry[key] = update[key]
        write_yaml(path, current)

    def _apply_review_queue(self, update: Any) -> None:
        if update is None:
            return
        if not isinstance(update, dict):
            raise StateUpdateError("review_queue update must be an object")
        path = self.state_dir / "review_queue.yaml"
        current = load_yaml(path)
        queue = current.setdefault("queue", [])
        if not isinstance(queue, list):
            raise StateUpdateError("review queue must be a list")

        remove_items = update.get("remove", []) or []
        add_items = update.get("add", []) or []
        if not isinstance(remove_items, list) or not isinstance(add_items, list):
            raise StateUpdateError("review_queue add/remove must be lists")

        queue[:] = [item for item in queue if item not in remove_items]
        for item in add_items:
            if item not in queue:
                queue.append(item)
        write_yaml(path, current)

    def _apply_lesson_note(self, update: Any, context: LearningContext) -> None:
        if update is None:
            return
        if not isinstance(update, dict):
            raise StateUpdateError("lesson_note update must be an object")
        lesson_id = update.get("lesson_id", context.curriculum.lesson_id)
        if lesson_id != context.curriculum.lesson_id:
            raise StateUpdateError("lesson_note lesson_id must match current lesson")

        path = self.state_dir / "lesson_notes" / f"{lesson_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_render_lesson_note(lesson_id, update))


def parse_state_update(raw_update: str) -> YamlMap:
    text = raw_update.strip()
    text = _strip_code_fence(text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise StateUpdateError(f"LLM returned invalid JSON state update: {exc}") from exc
    if not isinstance(data, dict):
        raise StateUpdateError("State update JSON must be an object")
    return data


def _strip_code_fence(text: str) -> str:
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1).strip() if match else text


def _find_or_create_lesson_entry(lessons: list[Any], lesson_id: str) -> YamlMap:
    for item in lessons:
        if isinstance(item, dict) and item.get("lesson_id") == lesson_id:
            return item
    entry: YamlMap = {"lesson_id": lesson_id}
    lessons.append(entry)
    return entry


def _render_lesson_note(lesson_id: str, update: YamlMap) -> str:
    summary = update.get("summary") or ""
    weak_points = update.get("weak_points") or []
    aha_moments = update.get("aha_moments") or []
    next_action = update.get("next_action") or ""
    return "\n".join(
        [
            f"# {lesson_id} Notes",
            "",
            "## Summary",
            str(summary),
            "",
            "## Weak Points",
            *[f"- {item}" for item in weak_points],
            "",
            "## Aha Moments",
            *[f"- {item}" for item in aha_moments],
            "",
            "## Next Action",
            str(next_action),
            "",
        ]
    )


def _phase_number(phase_id: str) -> int:
    if not phase_id.startswith("P") or not phase_id[1:].isdigit():
        raise StateUpdateError(f"Invalid phase id: {phase_id}")
    return int(phase_id[1:])

