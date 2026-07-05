from __future__ import annotations

from typing import Dict, Iterable, Mapping, Set

from backend.state.models import ASSESS_MODE, TEACH_MODE

from .curriculum_tools import (
    get_current_topic,
    get_student_learning_summary,
    search_curriculum,
)
from .models import ToolCall, ToolContext, ToolFunction, ToolResult


class ToolError(ValueError):
    pass


class ToolRegistry:
    def __init__(
        self,
        tools: Mapping[str, ToolFunction],
        mode_policy: Mapping[str, Iterable[str]],
    ) -> None:
        self._tools = dict(tools)
        self._mode_policy: Dict[str, Set[str]] = {
            mode: set(names) for mode, names in mode_policy.items()
        }

    def validate(self, mode: str, tool_call: ToolCall) -> None:
        if tool_call.name not in self._tools:
            raise ToolError(f"Unknown tool: {tool_call.name}")
        allowed_tools = self._mode_policy.get(mode)
        if allowed_tools is None:
            raise ToolError(f"No tools are allowed for mode: {mode}")
        if tool_call.name not in allowed_tools:
            raise ToolError(f"Tool {tool_call.name} is not allowed in mode: {mode}")
        if not isinstance(tool_call.arguments, dict):
            raise ToolError(f"Tool arguments for {tool_call.name} must be an object")

    def execute(self, mode: str, tool_call: ToolCall, context: ToolContext) -> ToolResult:
        self.validate(mode, tool_call)
        return self._tools[tool_call.name](tool_call, context)


def default_tool_registry() -> ToolRegistry:
    tools = {
        "get_current_topic": get_current_topic,
        "search_curriculum": search_curriculum,
        "get_student_learning_summary": get_student_learning_summary,
    }
    return ToolRegistry(
        tools=tools,
        mode_policy={
            TEACH_MODE: tools.keys(),
            ASSESS_MODE: [],
        },
    )
