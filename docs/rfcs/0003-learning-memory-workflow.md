# Status

Draft

# Problem

The CLI currently prints teaching output but does not persist it. As a result, later workflows cannot reliably access what was taught in the current lesson.

Once `MemoryStore` exists, teaching output should become raw learning evidence stored under `memory/`, while state updates should continue to flow only through `StateUpdater`.

# Motivation

Persisting teaching output is the next incremental step after adding `MemoryStore`.

The learner assessment workflow depends on retrieving the latest teaching output for the current lesson. Saving teaching output also makes local learning sessions easier to inspect, debug, and reproduce.

This work should introduce the memory write into the teaching flow without changing state schema or expanding the system into a broader session manager.

# Goals

- Keep `learn` working as the default teaching command.
- Add an explicit `learn teach` command for the same teaching workflow.
- Save teaching output to `MemoryStore` after the LLM returns it.
- Store teaching output with record type `teaching`.
- Include metadata such as:
  - phase
  - lesson_id
  - lesson_path when available
- Keep `StateUpdater` responsible only for state changes.
- Keep `MemoryStore` responsible only for raw evidence.
- Document the distinction between `state/` and `memory/`.

# Non-goals

- Do not implement learner response handling.
- Do not implement assessment.
- Do not change the state schema.
- Do not change `StateUpdater` responsibilities.
- Do not add embeddings, vector search, RAG, semantic memory, or a database server.
- Do not add a session manager.
- Do not add a web UI.
- Do not redesign the CLI beyond adding the explicit teaching command.

# Current State

The current CLI command is `learn`.

The teaching flow:

1. Loads `.env` if present.
2. Loads current navigation state.
3. Resolves the current curriculum lesson.
4. Loads current state context.
5. Builds a teaching prompt.
6. Calls the LLM.
7. Prints the teaching response.
8. Builds a state-update prompt using the teaching response.
9. Calls the LLM again.
10. Applies the returned state update through `StateUpdater`.

There is no memory persistence in this flow. Teaching output exists only in terminal output and as temporary in-process data used for the state-update prompt.

# Proposed Design

Introduce memory persistence into the teaching workflow after the teaching LLM call returns and before the state-update prompt is generated.

The CLI should support:

```text
learn
learn teach
```

Both commands should execute the same teaching workflow.

The teaching workflow should:

1. Load current learning context.
2. Build teaching prompt.
3. Call the LLM.
4. Print teaching output.
5. Save teaching output to `MemoryStore` as a `teaching` record.
6. Build state-update prompt.
7. Call the LLM for structured state update.
8. Apply the state update through `StateUpdater`.

The memory record should contain:

- `lesson_id`
- `record_type: teaching`
- teaching response as `content`
- metadata with phase, lesson id, and lesson path when available
- creation timestamp

Suggested storage location:

```text
memory/
  P0L1/
    teaching.json
```

Module responsibilities:

- CLI
  - Orchestrates the teaching workflow.
  - Decides when to save teaching output.
  - Does not serialize memory records directly.

- `MemoryStore`
  - Persists and retrieves teaching records.
  - Does not update `state/`.

- `StateUpdater`
  - Applies structured state updates.
  - Does not write to `memory/`.

- `PromptBuilder`
  - Continues to build teaching and state-update prompts.
  - Does not know where memory is stored.

# Alternatives Considered

Alternative 1: Keep teaching output terminal-only

- Advantages:
  - No new writes.
  - Current behavior remains unchanged.
  - No memory directory management.
- Disadvantages:
  - Assessment cannot retrieve teaching output.
  - Learning sessions are not auditable.
  - Debugging state updates is harder.
- Decision:
  - Not selected. The planned assessment workflow requires durable teaching output.

Alternative 2: Save teaching output in `state/lesson_notes/`

- Advantages:
  - Uses an existing directory.
  - Human-readable location.
  - Easy to inspect.
- Disadvantages:
  - Confuses raw evidence with learner notes.
  - Makes lesson notes less focused.
  - Couples memory evidence to state storage.
- Decision:
  - Not selected. `state/lesson_notes/` should remain human-readable derived state, not raw teaching evidence.

Alternative 3: Save teaching output directly from `StateUpdater`

- Advantages:
  - Centralizes writes after the LLM state-update step.
  - Avoids adding memory calls to CLI workflow.
  - May seem convenient because state updates already happen there.
- Disadvantages:
  - Violates the `StateUpdater` responsibility boundary.
  - Couples evidence storage to state mutation.
  - Makes future assessment workflows harder to reason about.
- Decision:
  - Not selected. `StateUpdater` should remain focused on state files only.

Alternative 4: Add a full session abstraction now

- Advantages:
  - Could group teaching, response, assessment, and state updates.
  - May help with future multi-step workflows.
  - Provides a natural place for timestamps and ordering.
- Disadvantages:
  - Larger design than the current issue requires.
  - Adds concepts before there is enough usage evidence.
  - Risks over-engineering a single-learner local CLI.
- Decision:
  - Not selected. The current need is simply to persist teaching output.

# Trade-offs

The proposed design adds a memory write to the teaching workflow. This makes the flow slightly more complex but provides the evidence needed for assessment.

Using a single `teaching` record path is simple, but it may overwrite previous teaching runs unless the accepted MemoryStore design chooses timestamped records. That trade-off should be resolved consistently with RFC 0001.

Adding `learn teach` introduces a clearer command structure while preserving `learn` as the simple default. This is a small CLI expansion that supports future explicit commands such as `learn assess`.

The workflow deliberately avoids a broader session model. That keeps the implementation small, but future work may need to revisit how multiple teaching and assessment records are grouped.

# Open Questions

- Should `learn` remain an alias for `learn teach` indefinitely?
- Should teaching output overwrite the latest `teaching.json` or create timestamped records?
- Should the saved teaching record include the full teaching prompt or only the model output?
- Should failed state-update generation still leave the teaching output saved?
- Should the CLI print the path of the saved teaching record?
- How should memory files be treated in Git for normal learner use?

