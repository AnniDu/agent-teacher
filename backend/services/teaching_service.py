from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from backend.curriculum.curriculum import Curriculum, Lesson, Topic
from backend.prompts.teaching_prompt import build_teaching_prompt, build_teaching_tool_result_prompt
from backend.state.models import TEACH_MODE, LearningState
from backend.tools.models import ToolCall, ToolContext, ToolResult
from backend.tools.registry import ToolError, ToolRegistry, default_tool_registry

from .llm_client import (
    LLMClient,
    TeachingResponse,
    TeachingToolRequest,
    generate_teaching_response,
)


@dataclass(frozen=True)
class TeachingResult:
    explanation: str
    question: str
    tool_call_event: Optional[Dict[str, Any]] = None

    @property
    def message(self) -> str:
        return f"{self.explanation}\n\n{self.question}"


class TeachingToolError(RuntimeError):
    def __init__(self, message: str, tool_call_event: Dict[str, Any]) -> None:
        super().__init__(message)
        self.tool_call_event = tool_call_event


class TeachingService:
    def __init__(self, llm: LLMClient, tool_registry: Optional[ToolRegistry] = None) -> None:
        self._llm = llm
        self._tool_registry = tool_registry or default_tool_registry()

    def teach(
        self,
        state: LearningState,
        curriculum: Curriculum,
        lesson: Lesson,
        topic: Topic,
    ) -> TeachingResult:
        response = generate_teaching_response(self._llm, build_teaching_prompt(state, lesson, topic))
        if isinstance(response, TeachingResponse):
            return TeachingResult(explanation=response.explanation, question=response.question)
        if not isinstance(response, TeachingToolRequest):
            raise ValueError("Unsupported teaching LLM response")

        tool_result, tool_event = self._execute_tool(
            response.tool_call,
            state,
            curriculum,
            lesson,
            topic,
        )
        final_response = generate_teaching_response(
            self._llm,
            build_teaching_tool_result_prompt(state, lesson, topic, tool_result),
        )
        if isinstance(final_response, TeachingToolRequest):
            event = dict(tool_event)
            event["succeeded"] = False
            event["error"] = "A second tool request is not allowed in one teaching turn"
            raise TeachingToolError(event["error"], event)
        if not isinstance(final_response, TeachingResponse):
            raise ValueError("Unsupported final teaching LLM response")
        return TeachingResult(
            explanation=final_response.explanation,
            question=final_response.question,
            tool_call_event=tool_event,
        )

    def _execute_tool(
        self,
        tool_call: ToolCall,
        state: LearningState,
        curriculum: Curriculum,
        lesson: Lesson,
        topic: Topic,
    ) -> Tuple[ToolResult, Dict[str, Any]]:
        event = {
            "tool_name": tool_call.name,
            "arguments": dict(tool_call.arguments),
            "succeeded": False,
        }
        try:
            result = self._tool_registry.execute(
                TEACH_MODE,
                tool_call,
                ToolContext(state=state, curriculum=curriculum, lesson=lesson, topic=topic),
            )
        except (ToolError, ValueError) as exc:
            event["error"] = str(exc)
            raise TeachingToolError(str(exc), event) from exc
        event["succeeded"] = True
        event["result_metadata"] = _compact_result_metadata(result)
        return result, event


def _compact_result_metadata(result: ToolResult) -> Dict[str, Any]:
    metadata = dict(result.metadata or {})
    if isinstance(result.content, dict) and "matches" in result.content:
        metadata["match_count"] = len(result.content.get("matches") or [])
    return metadata
