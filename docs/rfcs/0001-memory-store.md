# Status

Draft

# Problem

The project has clear file-based boundaries for curriculum content and learning state, but it does not yet have a dedicated place to store raw learning evidence.

The current `state/` directory is responsible for mutable learner state such as navigation, progress, review queue, and lesson notes. That state is derived from learning interactions. It should not also become the storage location for raw teaching outputs, learner responses, or assessment outputs.

Without a separate evidence store, future features that need to inspect prior teaching sessions or learner responses would either overload `state/` or couple directly to ad hoc files.

# Motivation

The next planned features require durable access to learning evidence:

- teaching output should be persisted after a teaching run
- learner responses should be saved before assessment
- assessment output should be saved before applying state updates

Introducing a small `MemoryStore` boundary first lets those features evolve incrementally without changing existing CLI behavior, state schema, or curriculum files.

# Goals

- Add a minimal file-based abstraction for storing raw learning evidence.
- Keep `state/` as the source of truth for learner state.
- Store raw evidence under `memory/`.
- Define a `MemoryRecord` shape with:
  - `record_id`
  - `lesson_id`
  - `record_type`
  - `content`
  - `metadata`
  - `created_at`
- Define a `MemoryStore` interface with:
  - `save(record)`
  - `get(record_id)`
  - `latest(lesson_id, record_type)`
- Provide a JSON-backed implementation suitable for local development.
- Preserve existing CLI behavior.

# Non-goals

- Do not persist teaching output yet.
- Do not implement learner responses.
- Do not implement learner assessment.
- Do not change `StateUpdater`.
- Do not change the state schema.
- Do not introduce embeddings, vector search, RAG, or semantic memory.
- Do not introduce a database server.
- Do not design a session manager.
- Do not design long-term analytics.

# Current State

The repository currently has these relevant boundaries:

- `curriculum/` contains modular, read-only lesson content.
- `state/navigation.yaml` identifies the current phase and lesson.
- `state/progress/phaseX.yaml` stores phase and lesson progress.
- `state/review_queue.yaml` stores review items.
- `state/lesson_notes/` stores human-readable lesson notes.
- `CurriculumLoader` loads only the current curriculum index, phase index, and lesson.
- `StateLoader` loads navigation, progress, review queue, and optional lesson notes.
- `PromptBuilder` constructs teaching and state-update prompts from loaded context.
- `LLMClient` isolates provider-specific LLM calls.
- `StateUpdater` parses structured state updates and writes only state files.
- The CLI currently teaches one lesson and applies a state update.

There is no `memory/` directory and no module responsible for raw evidence records.

# Proposed Design

Add a new module boundary: `MemoryStore`.

The `MemoryStore` is responsible only for raw learning evidence. It does not know how to load curriculum, build prompts, call the LLM, or update learner state.

The design has three concepts:

- `MemoryRecord`: a typed data object representing one evidence record.
- `MemoryStore`: an interface describing evidence storage operations.
- `JsonMemoryStore`: a local file-based implementation.

The initial storage layout should be simple and lesson-scoped:

```text
memory/
  P0L1/
    teaching.json
```

The store should use the `lesson_id` and `record_type` to group related evidence. The implementation may choose a stable filename for singleton record types such as `teaching`, while preserving the `record_id` inside the record.

Module responsibilities:

- `MemoryRecord`
  - Holds evidence metadata and content.
  - Does not perform file I/O.

- `MemoryStore`
  - Defines the persistence boundary.
  - Keeps callers independent of the file layout.

- `JsonMemoryStore`
  - Serializes and deserializes records as JSON.
  - Creates lesson directories as needed.
  - Implements `save`, `get`, and `latest`.
  - Does not modify `state/`.

Interactions:

1. A future workflow creates a `MemoryRecord`.
2. The workflow passes the record to `MemoryStore.save`.
3. Later workflows call `MemoryStore.get` or `MemoryStore.latest`.
4. State changes, if any, continue to go through `StateUpdater`.

# Alternatives Considered

Alternative 1: Store raw evidence inside `state/`

- Advantages:
  - Fewer directories.
  - No new storage abstraction.
  - Easy to inspect manually.
- Disadvantages:
  - Mixes derived state with raw evidence.
  - Makes state files grow for reasons unrelated to navigation or progress.
  - Encourages `StateUpdater` to take on evidence-storage responsibilities.
- Decision:
  - Not selected. The project already treats `state/` as source-of-truth learner state, so raw evidence should remain separate.

Alternative 2: Write ad hoc JSON files directly from CLI workflows

- Advantages:
  - Fastest implementation.
  - Minimal upfront code.
  - No interface to maintain.
- Disadvantages:
  - Couples CLI workflows to file layout.
  - Makes later changes harder if storage layout changes.
  - Risks inconsistent record structure across features.
- Decision:
  - Not selected. A small `MemoryStore` boundary is a common production pattern and keeps responsibilities clear without adding much complexity.

Alternative 3: Use SQLite for evidence storage

- Advantages:
  - Better querying.
  - Atomic writes.
  - More scalable if record volume grows.
- Disadvantages:
  - Adds operational and schema complexity.
  - Makes manual inspection less simple.
  - Solves problems the project does not yet have.
- Decision:
  - Not selected. The current project is one local learner and one linear curriculum, so file-based JSON is sufficient.

Alternative 4: Store evidence as Markdown

- Advantages:
  - Human-readable.
  - Easy to review in Git.
  - Good for narrative notes.
- Disadvantages:
  - Harder to parse reliably.
  - Weak fit for record metadata.
  - Makes `latest` and `get` behavior less predictable.
- Decision:
  - Not selected for raw evidence records. Markdown remains appropriate for human-readable lesson notes.

# Trade-offs

The proposed design adds one new module and one new top-level data directory. That is more structure than direct file writes, but it preserves module boundaries and prevents `state/` from becoming a mixed-purpose storage area.

JSON records are easy to read and test, but they are not a general query system. This is acceptable because the immediate requirements only need `save`, `get`, and `latest`.

The design intentionally avoids solving future semantic memory needs. If embeddings or search become necessary later, they can be added behind a separate design rather than hidden inside this initial store.

# Open Questions

- Should `record_id` be caller-provided, generated by the store, or both?
- Should singleton record types such as `teaching` overwrite the previous record or keep timestamped history?
- What timestamp format should `created_at` use?
- Should `latest` sort by `created_at`, filename timestamp, or both?
- Should `metadata` be constrained beyond being a mapping?
- Should `memory/` be committed to Git during normal use, or treated as local learner data?

