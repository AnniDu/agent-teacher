from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .curriculum import Curriculum, Lesson, Topic


class CurriculumLoader:
    def __init__(self, curriculum_dir: Path) -> None:
        self._curriculum_dir = curriculum_dir

    def load(self) -> Curriculum:
        lesson_paths = sorted(self._curriculum_dir.glob("phase*/*.md"))
        lessons = [self._load_lesson(path) for path in lesson_paths if path.name != "index.md"]
        return Curriculum(lessons)

    def _load_lesson(self, path: Path) -> Lesson:
        raw = path.read_text()
        metadata, body = _split_front_matter(raw)
        title = metadata.get("title") or _first_heading(body) or path.stem.replace("-", " ").title()
        topics = _extract_topics(body)
        if not topics:
            topics = [Topic(name=title, content=body.strip())]
        return Lesson(
            lesson_id=metadata.get("id", path.stem),
            phase_id=metadata.get("phase", path.parent.name.upper()),
            title=title.strip('"'),
            path=str(path),
            content=body.strip(),
            topics=topics,
            previous_lesson_id=_none_if_null(metadata.get("previous")),
            next_lesson_id=_none_if_null(metadata.get("next")),
        )


def _split_front_matter(raw: str) -> Tuple[Dict[str, str], str]:
    if not raw.startswith("---\n"):
        return {}, raw
    end = raw.find("\n---", 4)
    if end == -1:
        return {}, raw
    front_matter = raw[4:end]
    body = raw[end + len("\n---") :].lstrip()
    metadata: Dict[str, str] = {}
    for line in front_matter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, body


def _first_heading(body: str) -> Optional[str]:
    for line in body.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return None


def _extract_topics(body: str) -> List[Topic]:
    lines = body.splitlines()
    topics: List[Topic] = []
    for index, line in enumerate(lines):
        if line.strip().lower() != "topics":
            continue
        for topic_line in lines[index + 1 :]:
            stripped = topic_line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                break
            match = re.match(r"[-*]\s+(.+)", stripped)
            if match:
                name = match.group(1).strip()
                topics.append(Topic(name=name, content=_topic_content(name, body)))
                continue
            if topics:
                break
        break
    return topics


def _topic_content(topic_name: str, body: str) -> str:
    return f"Topic: {topic_name}\n\n{body.strip()}"


def _none_if_null(value: Optional[str]) -> Optional[str]:
    if value is None or value.lower() == "null":
        return None
    return value
