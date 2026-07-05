from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Topic:
    name: str
    content: str


@dataclass(frozen=True)
class Lesson:
    lesson_id: str
    phase_id: str
    title: str
    path: str
    content: str
    topics: List[Topic]
    previous_lesson_id: Optional[str] = None
    next_lesson_id: Optional[str] = None


class Curriculum:
    def __init__(self, lessons: List[Lesson], default_lesson_id: str = "P0L1") -> None:
        if not lessons:
            raise ValueError("Curriculum must contain at least one lesson")
        self._lessons = lessons
        self._by_id: Dict[str, Lesson] = {lesson.lesson_id: lesson for lesson in lessons}
        self._default_lesson_id = default_lesson_id if default_lesson_id in self._by_id else lessons[0].lesson_id

    def default_lesson(self) -> Lesson:
        return self.lesson(self._default_lesson_id)

    def lesson(self, lesson_id: str) -> Lesson:
        try:
            return self._by_id[lesson_id]
        except KeyError as exc:
            raise ValueError(f"Unknown lesson: {lesson_id}") from exc

    def topic(self, lesson_id: str, topic_name: str) -> Topic:
        lesson = self.lesson(lesson_id)
        for topic in lesson.topics:
            if topic.name == topic_name:
                return topic
        raise ValueError(f"Unknown topic for {lesson_id}: {topic_name}")

    def first_topic(self, lesson_id: str) -> str:
        lesson = self.lesson(lesson_id)
        if not lesson.topics:
            return lesson.title
        return lesson.topics[0].name

    def next_topic(self, lesson_id: str, topic_name: str) -> Optional[str]:
        lesson = self.lesson(lesson_id)
        names = [topic.name for topic in lesson.topics]
        try:
            index = names.index(topic_name)
        except ValueError as exc:
            raise ValueError(f"Unknown topic for {lesson_id}: {topic_name}") from exc
        next_index = index + 1
        if next_index >= len(names):
            return None
        return names[next_index]

    def content_for(self, lesson_id: str, topic_name: str) -> str:
        lesson = self.lesson(lesson_id)
        topic = self.topic(lesson_id, topic_name)
        return f"{lesson.title}\n\n{topic.content}\n\nFull lesson context:\n{lesson.content}"
