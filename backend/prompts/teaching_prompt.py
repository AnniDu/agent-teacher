from __future__ import annotations

from backend.curriculum.curriculum import Lesson, Topic
from backend.state.models import LearningState


def build_teaching_prompt(state: LearningState, lesson: Lesson, topic: Topic) -> str:
    return f"""You are helping a student learn an AI systems engineering topic.

Your task is bounded:
- Explain only the current topic.
- Ask one follow-up question.
- Do not decide workflow mode.
- Do not update state.
- Do not choose the next action.

Current phase: {state.current_phase}
Current lesson: {lesson.title}
Current topic: {topic.name}
Known misconceptions: {', '.join(state.misconceptions) if state.misconceptions else 'None'}

Curriculum content:
{topic.content}

Return JSON with exactly these keys:
{{
  "explanation": "short teaching explanation",
  "question": "one follow-up question"
}}
"""
