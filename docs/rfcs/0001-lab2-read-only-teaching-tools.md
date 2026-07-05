# RFC 0001: Lab 2 Read-Only Teaching Tools

Status: Proposed

Issue: #18

## Summary

Introduce one-step, LLM-selected, read-only tool calling inside the teaching workflow.

During a teaching turn, the LLM may request at most one approved read-only tool. The backend validates the request through a `ToolRegistry`, executes the tool if it is allowed for the current workflow mode, returns the tool result to the LLM, and asks the LLM for the final teaching response.

Tool calling is only available in teach mode for Lab 2. Assessment remains unchanged.

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

Returns the current phase, lesson, topic, and topic content.

#### `search_curriculum`

Arguments:

```json
{
  "query": "string"
}
```

Returns matching curriculum snippets from the existing curriculum module.

This is simple keyword search over the existing curriculum files, not RAG or vector search.

#### `get_student_learning_summary`

Arguments:

```json
{}
```

Returns a compact read-only summary from `LearningState`, such as:

* current phase
* current lesson
* current topic
* current mode
* understanding score
* misconceptions
* completed topics
* next step

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

The LLM response should be JSON.

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

## Error Handling

The backend should raise clear errors for:

* unknown tool names
* malformed tool arguments
* tools not allowed in the current mode
* a second tool request in the same teaching turn
* malformed LLM tool response

Errors should be deterministic backend errors, not LLM-decided behavior.

## Testing

Required tests:

* successful allowed tool call
* unknown tool rejection
* mode policy rejection
* max-one-tool-call behavior
* no state mutation from tools
* final teaching response without a tool call still works
* tool result is passed back into the LLM before final teaching response

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

* Should tool-call errors return HTTP 500 through the existing `/chat` endpoint, or should the API convert them into a structured client-facing error response?
* Should `search_curriculum` search the whole curriculum or only the current phase for Lab 2?
* Should tool calls be logged in the development event log, or should event logging remain limited to student messages, assistant messages, assessment results, and state transitions?
