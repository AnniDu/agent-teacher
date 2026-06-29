# Learning Coach Agent Design Document

## 1. Overall Architecture

The Lab 1 system is a simple stateful learning agent with an explicit backend-controlled workflow.

```text
Frontend Chat UI
    |
    | POST /chat
    v
Backend Controller
    |
    v
State Manager
    |
    v
Learning Control Loop
    |
    |-- Teaching Service -> LLM
    |
    |-- Assessment Service -> LLM
    |
    v
State Manager
    |
    v
Response to Frontend
```

The central architectural rule is:

> The backend decides what happens next. The LLM only performs bounded reasoning tasks.

Workflow mode is determined only by persisted backend state and deterministic transition logic. The LLM must never decide workflow mode, routing, state transitions, or the next action. The LLM should only perform bounded reasoning tasks such as teaching, assessment, and feedback generation.

## 2. Component Responsibilities

### Frontend

Responsibilities:

* Render chat messages.
* Send student messages to the backend.
* Display assistant responses.
* Optionally show simple state indicators later, such as current lesson or topic.

The frontend should not contain learning workflow logic. For Lab 1, a single chat page is enough.

### Backend

Responsibilities:

* Receive chat requests.
* Load learning state.
* Determine the current workflow mode from backend state.
* Call the appropriate service.
* Update learning state deterministically.
* Save learning state.
* Return the assistant response.

The backend is the agent runtime.

### LLM

Responsibilities:

* Generate teaching explanations.
* Generate follow-up questions.
* Assess student answers.
* Optionally provide feedback text.

The LLM should not:

* Choose workflow mode.
* Write state directly.
* Decide routing.
* Select the next action.
* Perform state transitions.
* Persist data.
* Call tools.
* Generate dynamic workflows.

## 3. Backend Request Flow

Recommended Lab 1 flow:

```text
POST /chat

1. Parse request.
2. Load learning state.
3. Append student message to short conversation context.
4. Inspect current_mode.
5. If current_mode == "teach":
   - Generate teaching response.
   - Generate follow-up question.
   - Save last_question.
   - Set current_mode = "assess".
   - Set next_step = "wait_for_answer".
6. If current_mode == "assess":
   - Assess student answer against last_question/current_topic.
   - Update understanding_score and misconceptions.
   - If score >= threshold:
     - Move to next topic.
     - Set current_mode = "teach".
     - Set next_step = "teach_next_topic".
   - Otherwise:
     - Keep current topic.
     - Set current_mode = "teach".
     - Set next_step = "reteach_current_topic".
7. Save learning state.
8. Append development events.
9. Return assistant response.
```

The proposed architecture is directionally appropriate:

```text
POST /chat
Controller
load_state()
decide_next_step()
teach() or assess()
update_state()
save_state()
response
```

One refinement is to avoid putting most logic directly into `decide_next_step()`. Use a small explicit `LearningLoop` module instead. That module owns deterministic control flow and delegates bounded reasoning to teaching and assessment services.

The loop should be intentionally lightweight. Do not introduce workflow engines, planners, agent frameworks, or additional orchestration layers for Lab 1. The point of the lab is a clear and testable learning loop, not maximum architectural flexibility.

Recommended shape:

```text
Controller
  -> StateManager.load()
  -> LearningLoop.run(state, student_message)
       -> TeachingService or AssessmentService
       -> deterministic state transition
  -> StateManager.save()
  -> response
```

This keeps the controller thin and makes the control loop easy to test.

## 4. Learning State Schema

Minimal Lab 1 state:

```json
{
  "student_id": "student_001",
  "current_phase": "phase_1",
  "current_lesson": "lesson_1",
  "current_topic": "explicit_control_loop",
  "current_mode": "teach",
  "last_question": null,
  "understanding_score": null,
  "misconceptions": [],
  "completed_topics": [],
  "next_step": "teach_current_topic",
  "turn_count": 0,
  "updated_at": "2026-06-28T00:00:00Z"
}
```

Recommended fields:

| Field | Purpose |
| --- | --- |
| `student_id` | Identifies the learner. |
| `current_phase` | Course phase. |
| `current_lesson` | Current lesson. |
| `current_topic` | Current topic being taught. |
| `current_mode` | Either `teach` or `assess`. |
| `last_question` | Question the student is answering. |
| `understanding_score` | Latest assessment score. |
| `misconceptions` | Known gaps for current topic. |
| `completed_topics` | Topics already passed. |
| `next_step` | Human-readable backend decision. |
| `turn_count` | Useful for debugging and later evaluation. |
| `updated_at` | State freshness. |

Suggested enum values:

```text
current_mode = "teach" | "assess"

next_step =
  "teach_current_topic"
  "wait_for_answer"
  "reteach_current_topic"
  "teach_next_topic"
  "lesson_complete"
```

For Lab 1, store state as JSON. It is easy to inspect, easy to test, and avoids database overhead.

## 5. API Design

### POST /chat

Primary endpoint for the chat loop.

Request:

```json
{
  "student_id": "student_001",
  "message": "I think an agent needs a loop that observes and acts."
}
```

Response:

```json
{
  "message": "Good. You identified the loop structure. The missing part is that the workflow is controlled by code, not by the model. Let's revisit that...",
  "state": {
    "current_phase": "phase_1",
    "current_lesson": "lesson_1",
    "current_topic": "explicit_control_loop",
    "current_mode": "teach",
    "understanding_score": 0.6,
    "next_step": "reteach_current_topic"
  }
}
```

For Lab 1, returning a partial state summary is useful for debugging. Later, this can be hidden or moved behind a debug flag.

### GET /state/{student_id}

Development endpoint for inspecting state.

Response:

```json
{
  "student_id": "student_001",
  "current_phase": "phase_1",
  "current_lesson": "lesson_1",
  "current_topic": "explicit_control_loop",
  "current_mode": "assess",
  "last_question": "What makes an agent control loop explicit?",
  "understanding_score": 0.7,
  "misconceptions": [],
  "completed_topics": [],
  "next_step": "wait_for_answer",
  "turn_count": 4,
  "updated_at": "2026-06-28T00:00:00Z"
}
```

### POST /state/{student_id}/reset

Development-only endpoint for Lab 1.

Request:

```json
{
  "phase": "phase_1",
  "lesson": "lesson_1",
  "topic": "explicit_control_loop"
}
```

Response:

```json
{
  "ok": true
}
```

This is useful while testing the loop repeatedly.

## 6. State Update Flow

The backend should update state in code, not by accepting arbitrary state mutations from the LLM.

Preferred assessment output from the LLM:

```json
{
  "score": 0.75,
  "feedback": "The student understands the loop but did not clearly distinguish reasoning from execution.",
  "misconceptions": [
    "The student may think the LLM controls the workflow."
  ]
}
```

Backend code then applies deterministic rules:

```python
if assessment.score >= 0.8:
    mark_topic_complete()
    move_to_next_topic()
    state.current_mode = "teach"
    state.next_step = "teach_next_topic"
else:
    state.current_mode = "teach"
    state.next_step = "reteach_current_topic"
```

This preserves separation between reasoning and workflow execution.

## 7. Event Log

Add a minimal append-only event log for debugging and future evaluation.

Recommended path:

```text
data/events/{student_id}.jsonl
```

Each line should be a small JSON object. Suggested event types:

* `student_message`
* `assistant_message`
* `assessment_result`
* `state_transition`

Example events:

```json
{"type":"student_message","student_id":"student_001","message":"I think the backend owns the loop.","created_at":"2026-06-28T00:00:00Z"}
{"type":"state_transition","student_id":"student_001","from_mode":"assess","to_mode":"teach","next_step":"reteach_current_topic","created_at":"2026-06-28T00:00:01Z"}
```

The event log is a development artifact. It should help inspect the loop and support later evaluation, but it should not become long-term memory, RAG context, or a second source of truth for learning state.

## 8. Module Design

Suggested backend modules:

```text
backend/
  app.py
  api/
    routes.py
    schemas.py
  core/
    learning_loop.py
    transitions.py
  services/
    teaching_service.py
    assessment_service.py
    llm_client.py
  state/
    state_manager.py
    state_store.py
    models.py
  events/
    event_log.py
  curriculum/
    curriculum_loader.py
    curriculum.py
  prompts/
    teaching_prompt.py
    assessment_prompt.py
  tests/
```

### api/routes.py

Defines REST endpoints.

Responsibilities:

* Parse requests.
* Call application services.
* Return responses.
* Avoid business logic.

### api/schemas.py

Defines request and response schemas.

Examples:

* `ChatRequest`
* `ChatResponse`
* `StateResponse`
* `ResetStateRequest`

### core/learning_loop.py

The central control loop.

Responsibilities:

* Receive `state` and `student_message`.
* Decide whether to teach or assess.
* Call the right service.
* Apply state transitions.
* Return assistant message and updated state.

This is the most important module for Lab 1.

### core/transitions.py

Pure state transition helpers.

Responsibilities:

* Move to assess mode.
* Move to next topic.
* Reteach current topic.
* Mark topic complete.
* Increment turn count.

Keeping these as pure functions makes the workflow easy to test.

### services/teaching_service.py

Responsibilities:

* Build teaching prompt.
* Call LLM.
* Return explanation and question.

Example return object:

```json
{
  "explanation": "...",
  "question": "..."
}
```

### services/assessment_service.py

Responsibilities:

* Build assessment prompt.
* Call LLM.
* Parse structured assessment result.
* Return score, feedback, and misconceptions.

It should not update state directly.

### services/llm_client.py

Responsibilities:

* Wrap the model provider.
* Expose one simple method, for example `generate(prompt: str) -> str`.

Later this can evolve to support structured output or tool calls.

### state/state_manager.py

Responsibilities:

* Load state by `student_id`.
* Create initial state if none exists.
* Save updated state.
* Validate state shape.

### state/state_store.py

Responsibilities:

* File-based persistence for Lab 1.
* Later replacement with SQLite or Postgres without changing the learning loop.

For Lab 1:

```text
data/students/student_001/state.json
```

### state/models.py

Defines state data structures.

Examples:

* `LearningState`
* `AssessmentResult`
* `TeachingResult`

### events/event_log.py

Append-only development log.

Responsibilities:

* Append student message events.
* Append assistant message events.
* Append assessment result events.
* Append state transition events.
* Write JSONL records to `data/events/{student_id}.jsonl`.

This module should stay simple. It is not memory, retrieval, analytics infrastructure, or a durable audit system for Lab 1.

### curriculum/curriculum_loader.py

Responsibilities:

* Parse the existing `curriculum/` files.
* Construct lightweight curriculum objects from the existing course, phase, lesson, lab, and topic hierarchy.
* Keep the existing curriculum format as the source of truth.

Do not invent a new curriculum schema for Lab 1 unless the existing format has a fundamental limitation.

### curriculum/curriculum.py

Lightweight curriculum models and read APIs.

Responsibilities:

* Expose traversal/query APIs required by the learning loop.
* Provide lesson and topic content for teaching and assessment.
* Provide deterministic topic ordering for progression.
* Keep curriculum knowledge out of API routes, services, and prompts.

The learning loop should consume curriculum only through this module.

### prompts/

Responsibilities:

* Store prompt templates.
* Keep prompt text separate from workflow logic.

## 9. Suggested Directory Structure

```text
learning-coach/
  README.md
  backend/
    app.py
    api/
      routes.py
      schemas.py
    core/
      learning_loop.py
      transitions.py
    services/
      llm_client.py
      teaching_service.py
      assessment_service.py
    state/
      models.py
      state_manager.py
      state_store.py
    events/
      event_log.py
    curriculum/
      curriculum.py
      curriculum_loader.py
    prompts/
      teaching_prompt.py
      assessment_prompt.py
    tests/
      test_learning_loop.py
      test_state_transitions.py
      test_state_manager.py
  frontend/
    index.html
    src/
      App.jsx
      api.js
      Chat.jsx
  data/
    students/
    events/
```

If using a Python-only MVP, the frontend can be skipped initially or built as a tiny static page.

The existing repository-level `curriculum/` directory remains the source of truth for course content. The `backend/curriculum/` module is an adapter around that content, not a replacement for it.

## 10. Future Extension Strategy

The architecture should evolve by replacing or extending modules, not rewriting the control loop.

### Tool Calling

Add later inside service modules, not the controller.

```text
TeachingService -> LLMClient -> ToolExecutor
```

The learning loop still decides when teaching happens.

### Structured Output

Add structured response parsing to:

* `TeachingService`
* `AssessmentService`

The control loop remains unchanged.

### Memory

Add a separate `MemoryStore`.

```text
LearningLoop
  -> StateManager for current state
  -> MemoryStore for historical events
```

Do not overload learning state with long-term memory.

The Lab 1 event log should not be treated as memory. If long-term memory is added later, it should be introduced as a separate explicit subsystem with clear read/write semantics.

### RAG

Add retrieval inside `TeachingService`.

```text
TeachingService
  -> Retriever
  -> LLM
```

The backend still controls the workflow.

### Planning

Add a planner later as a bounded reasoning service.

```text
PlanningService.suggest_next_topic(state)
```

The backend should still decide whether to accept the plan.

### Human-in-the-loop

Add a mode such as:

```text
current_mode = "awaiting_review"
```

The learning loop can pause until instructor approval.

### Evaluation

Use the JSONL event log and test fixtures as the starting point for later evaluation. Evaluation should be added as a separate capability after the MVP loop works end to end.

## 11. Design Trade-offs

### Explicit Control Loop vs. LLM-Driven Agent

Chosen: explicit backend control loop.

Why:

* Matches the learning objective.
* Easy to test.
* Easy to debug.
* Prevents the LLM from silently changing workflow behavior.

Alternative:

* Let the LLM decide the next action.

Trade-off:

* LLM-driven agents are more flexible but less deterministic.
* For Lab 1, flexibility is less important than architectural clarity.

### File-Based State vs. Database

Chosen: JSON file state.

Why:

* Simple.
* Inspectable.
* No infrastructure.
* Good enough for a local MVP.

Alternative:

* SQLite or Postgres.

Trade-off:

* File state is not ideal for concurrent users.
* Database state is more robust but adds setup and schema complexity.

For Lab 1, file state is appropriate.

### Single /chat Endpoint vs. Multiple Workflow Endpoints

Chosen: single `/chat` endpoint.

Why:

* Matches the user experience.
* Keeps frontend simple.
* Lets backend own mode selection.

Alternative:

```text
POST /teach
POST /assess
POST /next
```

Trade-off:

* Separate endpoints make actions explicit externally.
* A single endpoint better demonstrates a stateful agent loop.

For Lab 1, use `/chat`.

### Separate Teaching and Assessment Services

Chosen: separate services.

Why:

* Clear reasoning boundaries.
* Different prompts.
* Different output formats.
* Easier tests.

Alternative:

* One generic `LLMService`.

Trade-off:

* Separate services add a little structure.
* A generic service is simpler initially but becomes vague quickly.

For Lab 1, separate services are worth it.

### State Transitions in Code vs. LLM Output

Chosen: transitions in code.

Why:

* Deterministic.
* Testable.
* Prevents malformed LLM output from corrupting workflow.
* Reinforces separation of reasoning from execution.

Alternative:

* Ask the LLM to return the next state.

Trade-off:

* LLM-generated state is flexible.
* Code-generated state is safer and clearer.

For Lab 1, code-owned state transitions are the right choice.

### Minimal Event Log vs. No Event Log

Chosen: simple append-only JSONL event log.

Why:

* Makes the control loop easier to debug.
* Creates useful artifacts for later evaluation.
* Requires little infrastructure.
* Does not change the learning state model.

Alternative:

* No event log in Lab 1.

Trade-off:

* No event log is simpler.
* A minimal event log adds a small module and file writes, but gives much better visibility into state transitions.

For Lab 1, the event log is appropriate as long as it remains a development artifact and does not become memory or RAG.

### Existing Curriculum Format vs. New Curriculum Schema

Chosen: adapt the backend curriculum module to the existing `curriculum/` directory.

Why:

* The course structure already exists.
* Avoids redesigning content representation during Lab 1.
* Keeps curriculum content as a single source of truth.
* Lets the learning loop rely on simple read APIs without knowing file layout details.

Alternative:

* Create a new JSON curriculum schema for the learning coach.

Trade-off:

* A new schema could be easier for the app to parse.
* It would duplicate or replace existing course content and expand Lab 1 scope unnecessarily.

For Lab 1, the existing curriculum format should remain the source of truth unless implementation reveals a fundamental limitation.

## 12. Potential Risks

### State Drift

The state may become inconsistent if updates are scattered across modules.

Mitigation:

* Centralize transitions in `learning_loop.py` and `transitions.py`.

### Prompt Output Instability

The LLM may return malformed assessment output.

Mitigation:

* Use simple structured JSON.
* Validate parsed output.
* Fall back to a safe score or error response.

### Too Much Abstraction Too Early

It is tempting to add planners, memory, tools, or LangGraph now.

Mitigation:

* Keep Lab 1 focused on the explicit loop.
* Add extension points only where they naturally fit.

### Weak Assessment Quality

The assessment may be pedagogically shallow.

Mitigation:

* Accept this for Lab 1.
* The goal is agent architecture, not tutor quality.

### Hidden Workflow Logic in Prompts

Prompts may accidentally ask the LLM to decide what happens next.

Mitigation:

* Prompts should ask only for bounded outputs.
* Backend code should own all mode changes.

### Curriculum Drift

The backend could accidentally grow a second curriculum representation that diverges from the existing course files.

Mitigation:

* Treat `curriculum/` as the source of truth.
* Keep parsing and traversal inside the curriculum module.
* Do not duplicate curriculum hierarchy in API routes, services, prompts, or state files.

## 13. Recommendations Before Implementation

1. Start with the backend learning loop before building the frontend.
2. Write tests for the control loop first:
   - teach mode switches to assess mode
   - assess with high score moves to next topic
   - assess with low score reteaches current topic
   - state is saved after each turn
3. Keep the first state store file-based.
4. Use strict service boundaries:
   - teaching service teaches
   - assessment service assesses
   - state manager persists
   - learning loop controls workflow
5. Keep prompts simple and explicit.
6. Build the curriculum module around the existing `curriculum/` directory.
7. Add a minimal JSONL event log for development visibility.
8. Avoid adding memory, RAG, tools, planners, agent frameworks, or workflow engines in Lab 1.
9. Make state visible during development through `GET /state/{student_id}`.
10. Treat every chat request as one control-loop iteration.

The best Lab 1 implementation is not the smartest tutor. It is the clearest working example of a stateful AI agent with explicit backend-owned control flow.
