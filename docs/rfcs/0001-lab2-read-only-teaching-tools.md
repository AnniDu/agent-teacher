# RFC 0001: Lab 2 Read-Only Teaching Tools

Status: Proposed

Issue: #18

## Summary

Introduce one-step, LLM-selected, read-only tool calling inside the internal teaching workflow.

During a teaching turn, the LLM may request at most one approved read-only tool. The backend validates the request through a `ToolRegistry`, executes the tool if it is allowed for the current workflow mode, returns the tool result to the LLM, and asks the LLM for the final teaching response.

Tool calling is only available in teach mode for Lab 2. Assessment remains unchanged. The external `/chat` API contract does not change.

## Problem

The Lab 1 backend owns the learning loop and passes curriculum context directly into `TeachingService`. This keeps the workflow explicit, but it means teaching cannot request additional approved context when needed.

Lab 2 should introduce controlled tool calling without weakening the architecture:

* the backend still owns workflow control
* the LLM still cannot mutate state or choose routing
* tools are read-only and policy-checked
* only teaching can use tools
* only one tool call is allowed per teaching turn

## Goals

* Add LLM-selected tool calling to `TeachingService`.
* Add a `ToolRegistry` that validates tool names, mode policy, and arguments.
* Add structured tool request and tool result schemas.
* Add read-only teach-mode tools:
  * `get_current_topic`
  * `search_curriculum`
  * `get_student_learning_summary`
* Pass tool results back into the LLM for final teaching response generation.
* Preserve backend-owned workflow control and deterministic state transitions.
* Keep the external `/chat` request and response schema unchanged.

## Non-Goals

* No tool calling in assessment.
* No write tools.
* No RAG.
* No web search.
* No planner.
* No multi-agent workflow.
* No workflow engine.
* No state mutation from tools.
* No external side effects.
* No tool-driven curriculum advancement.

## Architecture

The teaching workflow becomes:

```text
LearningLoop
  -> TeachingService.teach(state, lesson, topic)
       -> LLM initial teaching/tool prompt
       -> if LLM returns final teaching response:
            return TeachingResult
       -> if LLM requests one tool:
            ToolRegistry.validate(mode="teach", tool_call)
            ToolRegistry.execute(tool_call, context)
            LLM final teaching prompt with tool result
            return TeachingResult
  -> deterministic transition_to_assess()
```

The `LearningLoop` remains the workflow owner. It only receives a `TeachingResult` from `TeachingService` and then applies the existing deterministic transition to assess mode.

Tool calling is internal to `TeachingService`. API routes, request schemas, response schemas, and frontend behavior should not know whether a teaching response used a tool.

## Module Design

### `backend/tools/models.py`

Defines structured tool data:

```python
ToolCall
ToolResult
ToolContext
```

`ToolCall` should include:

* `name`
* `arguments`

`ToolResult` should include:

* `name`
* `content`
* optional `metadata`

`ToolContext` should include read-only references needed by tools:

* current learning state
* curriculum
* current lesson
* current topic

Tool context is read-only. Tool functions receive context so they can construct a result, not so they can update workflow state or persistence.

### `backend/tools/registry.py`

Owns tool validation and execution.

Responsibilities:

* register approved tools
* enforce mode policy
* validate tool names
* validate tool arguments
* execute tools through a single backend-controlled entry point
* reject disallowed tools with clear errors

The registry must not mutate state or persist data.

### `backend/tools/curriculum_tools.py`

Contains the initial read-only teach-mode tools.

#### `get_current_topic`

Arguments:

```json
{}
```

Returns the current phase, lesson, topic, and full current topic content.

This tool exists so the initial teaching prompt can stay compact. The first teaching prompt should include enough context for the LLM to decide whether it can teach directly, but it should not duplicate the full topic content already available through `get_current_topic`. When the LLM needs the full topic text, it should request this tool.

#### `search_curriculum`

Arguments:

```json
{
  "query": "string"
}
```

Returns matching curriculum snippets from the existing curriculum module.

This is simple keyword search over the existing curriculum files, not RAG or vector search.

For Lab 2, search should prioritize the current phase:

1. Search lessons and lab files in the current phase first.
2. If fewer than the maximum result count are found, optionally include matches from other phases.

The result must be bounded. Return at most 3 compact matches. Each match should include:

* source metadata, such as phase, lesson id, title, and path
* a short excerpt
* the matched topic or section when available

The tool should not return full lesson files.

#### `get_student_learning_summary`

Arguments:

```json
{}
```

Returns a compact read-only summary from `LearningState`, such as:

* understanding score
* misconceptions
* completed topics
* weak topics when available
* recent wrong questions when available

This tool should return a curated learner-understanding summary, not raw workflow-control state. It should avoid exposing `next_step`, `current_mode`, or other backend routing/control fields to the LLM. It may include current lesson/topic identifiers only when useful as context for interpreting the learner's understanding.

This tool reads state but does not update it.

## Tool Policy

Tool policy is mode-based.

For Lab 2:

```text
teach:
  - get_current_topic
  - search_curriculum
  - get_student_learning_summary

assess:
  - no tools
```

Requests for tools outside the allowed mode must fail with a clear error.

## LLM Protocol

`TeachingService` should ask the LLM for either:

1. a final teaching response, or
2. one tool request

`TeachingService` should consume a provider-neutral internal response model, not provider-specific payloads. Gemini native function calling, JSON prompting, or JSON parsing should be hidden behind `LLMClient` or a small adapter owned by the LLM boundary.

The internal response model should represent one of:

* `TeachingResponse`
* `TeachingToolRequest`

Provider-specific details must not leak into `TeachingService`.

Final teaching response:

```json
{
  "type": "teaching_response",
  "explanation": "short teaching explanation",
  "question": "one follow-up question"
}
```

Tool request:

```json
{
  "type": "tool_call",
  "tool": {
    "name": "get_current_topic",
    "arguments": {}
  }
}
```

After executing a tool, `TeachingService` sends the tool result to the LLM and requires a final teaching response. A second tool request in the same teaching turn must be rejected.

## State and Persistence

Tools must be read-only.

They must not:

* mutate `LearningState`
* save state
* append events
* advance curriculum
* write files
* call external services

Existing state persistence remains owned by `StateManager`.

Existing event persistence remains owned by `LearningLoop`.

Tool calls should be appended to the development event log as `tool_call` events. A `tool_call` event should include:

* requested tool name
* sanitized arguments
* whether execution succeeded
* error message when execution fails

Tool result content should be kept compact in events. Avoid writing large curriculum excerpts into the event log.

Tool functions and `ToolRegistry` must not append events directly. They remain read-only and side-effect-free apart from returning a `ToolResult` or raising a validation/execution error. Event logging should be performed by the existing workflow/event owner, preferably `LearningLoop`, after `ToolRegistry` execution. If `LearningLoop` needs tool-call details, `TeachingService` may return tool-call metadata alongside `TeachingResult`.

## Error Handling

The backend should raise clear errors for:

* unknown tool names
* malformed tool arguments
* tools not allowed in the current mode
* a second tool request in the same teaching turn
* malformed LLM tool response

Errors should be deterministic backend errors, not LLM-decided behavior.

For Lab 2, tool-call failures can use the existing backend error path. Structured client-facing error responses can be deferred until a later issue.

## Testing

Required tests:

* successful allowed tool call
* unknown tool rejection
* mode policy rejection
* max-one-tool-call behavior
* no state mutation from tools
* final teaching response without a tool call still works
* tool result is passed back into the LLM before final teaching response
* `search_curriculum` returns at most 3 compact snippets and prioritizes the current phase
* tool calls append `tool_call` events through the workflow/event owner, not from tool functions
* `get_student_learning_summary` omits `next_step` and other workflow-control fields
* `TeachingService` consumes provider-neutral LLM response models
* `/chat` request and response schemas remain unchanged

Existing tests for:

* teach to assess transition
* assessment transitions
* state persistence
* frontend/API serving

should continue to pass.

## Implementation Notes

Keep the implementation small:

* no new third-party dependencies
* no workflow engine
* no planner
* no generic agent framework
* no async tool runtime

The first implementation should be a simple synchronous registry with explicit read-only tool functions.

## Open Questions

Resolved for Lab 2:

* Tool-call failures use the existing backend error path. Structured client-facing errors are deferred.
* `search_curriculum` searches the current phase first and returns at most 3 compact snippets.
* Tool calls are logged as `tool_call` events in the development event log by the workflow/event owner, not by tools.
* Tool calling remains internal to `TeachingService`; the external `/chat` API does not change.
