from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

from backend.curriculum.curriculum import Lesson, Topic
from backend.prompts.assessment_prompt import build_assessment_prompt
from backend.state.models import LearningState

from .llm_client import LLMClient


@dataclass(frozen=True)
class AssessmentResult:
    score: float
    feedback: str
    misconceptions: List[str]


class AssessmentService:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def assess(
        self,
        state: LearningState,
        lesson: Lesson,
        topic: Topic,
        student_message: str,
    ) -> AssessmentResult:
        raw = self._llm.generate(build_assessment_prompt(state, lesson, topic, student_message))
        data = _parse_json_object(raw)
        score = _clamp_score(data.get("score", 0.0))
        feedback = str(data.get("feedback") or "I could not assess the answer clearly.").strip()
        misconceptions = data.get("misconceptions") or []
        if not isinstance(misconceptions, list):
            misconceptions = [str(misconceptions)]
        return AssessmentResult(
            score=score,
            feedback=feedback,
            misconceptions=[str(item) for item in misconceptions],
        )


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


def _clamp_score(value: object) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return min(1.0, max(0.0, score))
