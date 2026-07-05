from __future__ import annotations

import json
from dataclasses import dataclass

from backend.curriculum.curriculum import Lesson, Topic
from backend.prompts.teaching_prompt import build_teaching_prompt
from backend.state.models import LearningState

from .llm_client import LLMClient


@dataclass(frozen=True)
class TeachingResult:
    explanation: str
    question: str

    @property
    def message(self) -> str:
        return f"{self.explanation}\n\n{self.question}"


class TeachingService:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def teach(self, state: LearningState, lesson: Lesson, topic: Topic) -> TeachingResult:
        raw = self._llm.generate(build_teaching_prompt(state, lesson, topic))
        data = _parse_json_object(raw)
        explanation = str(data.get("explanation") or raw).strip()
        question = str(data.get("question") or "What is your understanding of this topic?").strip()
        return TeachingResult(explanation=explanation, question=question)


def _parse_json_object(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        return {}
