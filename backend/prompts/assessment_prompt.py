from __future__ import annotations

from backend.curriculum.curriculum import Lesson, Topic
from backend.state.models import LearningState


def build_assessment_prompt(
    state: LearningState,
    lesson: Lesson,
    topic: Topic,
    student_message: str,
) -> str:
    return f"""Assess the student's answer to the current learning question.

Your task is bounded:
- Evaluate the answer.
- Generate concise feedback.
- Identify misconceptions.
- Do not decide workflow mode.
- Do not update state.
- Do not choose the next action.

Current phase: {state.current_phase}
Current lesson: {lesson.title}
Current topic: {topic.name}
Question asked: {state.last_question}

Curriculum content:
{topic.content}

Student answer:
{student_message}

Return JSON with exactly these keys:
{{
  "score": 0.0,
  "feedback": "short feedback for the student",
  "misconceptions": ["misconception if any"]
}}

Score must be a number from 0.0 to 1.0.
"""
