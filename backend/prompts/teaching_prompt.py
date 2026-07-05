from __future__ import annotations

from backend.curriculum.curriculum import Lesson, Topic
from backend.state.models import LearningState
from backend.tools.models import ToolResult


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

Available read-only tools in teach mode:
- get_current_topic: fetch full current topic content when needed.
- search_curriculum: search compact snippets, current phase first.
- get_student_learning_summary: fetch a curated learner-understanding summary.

If you have enough context, return JSON:
{{
  "type": "teaching_response",
  "explanation": "short teaching explanation",
  "question": "one follow-up question"
}}

If you need one tool, return JSON:
{{
  "type": "tool_call",
  "tool": {{
    "name": "get_current_topic",
    "arguments": {{}}
  }}
}}
"""


def build_teaching_tool_result_prompt(
    state: LearningState,
    lesson: Lesson,
    topic: Topic,
    tool_result: ToolResult,
) -> str:
    return f"""You are helping a student learn an AI systems engineering topic.

Your task is bounded:
- Explain only the current topic.
- Ask one follow-up question.
- Do not decide workflow mode.
- Do not update state.
- Do not choose the next action.
- Do not request another tool.

Current phase: {state.current_phase}
Current lesson: {lesson.title}
Current topic: {topic.name}
Known misconceptions: {', '.join(state.misconceptions) if state.misconceptions else 'None'}

Tool result:
{tool_result.content}

Return JSON:
{{
  "type": "teaching_response",
  "explanation": "short teaching explanation",
  "question": "one follow-up question"
}}
"""
