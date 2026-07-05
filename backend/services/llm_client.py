from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol, Union

from backend.config import Settings
from backend.tools.models import ToolCall


@dataclass(frozen=True)
class TeachingResponse:
    explanation: str
    question: str


@dataclass(frozen=True)
class TeachingToolRequest:
    tool_call: ToolCall


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


TeachingLlmResponse = Union[TeachingResponse, TeachingToolRequest]


def generate_teaching_response(llm: LLMClient, prompt: str) -> TeachingLlmResponse:
    raw = llm.generate(prompt)
    return parse_teaching_response(raw)


def parse_teaching_response(raw: str) -> TeachingLlmResponse:
    data = _parse_json_object(raw)
    response_type = data.get("type")
    if response_type == "tool_call":
        tool = data.get("tool")
        if not isinstance(tool, dict):
            raise ValueError("Malformed teaching tool response: missing tool object")
        name = tool.get("name")
        arguments = tool.get("arguments", {})
        if not isinstance(name, str) or not name:
            raise ValueError("Malformed teaching tool response: missing tool name")
        if not isinstance(arguments, dict):
            raise ValueError("Malformed teaching tool response: arguments must be an object")
        return TeachingToolRequest(tool_call=ToolCall(name=name, arguments=arguments))

    if response_type == "teaching_response" or "explanation" in data or "question" in data:
        explanation = str(data.get("explanation") or raw).strip()
        question = str(data.get("question") or "What is your understanding of this topic?").strip()
        return TeachingResponse(explanation=explanation, question=question)

    return TeachingResponse(
        explanation=raw.strip(),
        question="What is your understanding of this topic?",
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


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model

    def generate(self, prompt: str) -> str:
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )
        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
        request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode())
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Gemini request failed: {exc}") from exc

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Gemini response did not contain text") from exc
