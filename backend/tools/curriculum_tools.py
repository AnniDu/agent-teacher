from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from .models import ToolCall, ToolContext, ToolResult


MAX_SEARCH_RESULTS = 3
MAX_EXCERPT_LENGTH = 220


def get_current_topic(tool_call: ToolCall, context: ToolContext) -> ToolResult:
    _require_no_arguments(tool_call)
    return ToolResult(
        name=tool_call.name,
        content={
            "phase": context.lesson.phase_id,
            "lesson_id": context.lesson.lesson_id,
            "lesson_title": context.lesson.title,
            "topic": context.topic.name,
            "content": context.topic.content,
        },
        metadata={"lesson_path": context.lesson.path},
    )


def search_curriculum(tool_call: ToolCall, context: ToolContext) -> ToolResult:
    query = tool_call.arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("search_curriculum requires a non-empty string query")

    current_phase = context.lesson.phase_id
    lessons = context.curriculum.lessons()
    ordered_lessons = [
        lesson for lesson in lessons if lesson.phase_id == current_phase
    ] + [lesson for lesson in lessons if lesson.phase_id != current_phase]

    matches: List[Dict[str, Any]] = []
    seen: set = set()
    for lesson in ordered_lessons:
        lesson_matches = _matches_for_lesson(query, lesson)
        for topic_name, excerpt in lesson_matches:
            key = (lesson.lesson_id, topic_name, excerpt)
            if key in seen:
                continue
            seen.add(key)
            matches.append(
                {
                    "phase": lesson.phase_id,
                    "lesson_id": lesson.lesson_id,
                    "lesson_title": lesson.title,
                    "path": lesson.path,
                    "matched_topic_or_section": topic_name,
                    "excerpt": excerpt,
                }
            )
            if len(matches) >= MAX_SEARCH_RESULTS:
                return ToolResult(
                    name=tool_call.name,
                    content={"query": query.strip(), "matches": matches},
                    metadata={"max_results": MAX_SEARCH_RESULTS},
                )

    return ToolResult(
        name=tool_call.name,
        content={"query": query.strip(), "matches": matches},
        metadata={"max_results": MAX_SEARCH_RESULTS},
    )


def get_student_learning_summary(tool_call: ToolCall, context: ToolContext) -> ToolResult:
    _require_no_arguments(tool_call)
    state = context.state
    weak_topics = []
    if state.understanding_score is not None and state.understanding_score < 0.7:
        weak_topics.append(state.current_topic)
    recent_wrong_questions = [state.last_question] if state.misconceptions and state.last_question else []
    return ToolResult(
        name=tool_call.name,
        content={
            "student_id": state.student_id,
            "current_lesson": state.current_lesson,
            "current_topic": state.current_topic,
            "understanding_score": state.understanding_score,
            "misconceptions": list(state.misconceptions),
            "completed_topics": list(state.completed_topics),
            "weak_topics": weak_topics,
            "recent_wrong_questions": recent_wrong_questions,
        },
    )


def _require_no_arguments(tool_call: ToolCall) -> None:
    if tool_call.arguments:
        raise ValueError(f"{tool_call.name} does not accept arguments")


def _matches_for_lesson(query: str, lesson: Any) -> List[Tuple[str, str]]:
    normalized_query = query.strip().lower()
    matches: List[Tuple[str, str]] = []
    for topic in lesson.topics:
        index = topic.content.lower().find(normalized_query)
        if index != -1:
            matches.append((topic.name, _excerpt(topic.content, index, len(normalized_query))))
    if normalized_query in lesson.title.lower():
        matches.append((lesson.title, _excerpt(lesson.content, 0, len(normalized_query))))
    if not matches:
        index = lesson.content.lower().find(normalized_query)
        if index != -1:
            matches.append((lesson.title, _excerpt(lesson.content, index, len(normalized_query))))
    return matches


def _excerpt(text: str, start: int, length: int) -> str:
    left = max(0, start - 80)
    right = min(len(text), start + length + 120)
    excerpt = re.sub(r"\s+", " ", text[left:right]).strip()
    if left > 0:
        excerpt = f"...{excerpt}"
    if right < len(text):
        excerpt = f"{excerpt}..."
    if len(excerpt) > MAX_EXCERPT_LENGTH:
        excerpt = excerpt[: MAX_EXCERPT_LENGTH - 3].rstrip() + "..."
    return excerpt
