# Status

Draft

# Problem

The current learning flow can teach a lesson and ask the LLM for a structured state update, but state changes are not grounded in learner evidence.

The system needs a workflow that reads a learner response, compares it with the current lesson goal and recent teaching output, and updates learner state only when there is evidence from the learner.

Without this boundary, the system may infer progress from teaching output alone, which is not a reliable indicator of learner understanding.

# Motivation

Learner assessment is needed after teaching output is persisted to memory. Once the system can retrieve the latest teaching output, it can evaluate a learner response against the actual lesson context and teaching session.

This work supports a simple teach-then-assess loop:

1. Teach the current lesson.
2. Save the teaching output.
3. Read a learner response.
4. Assess the response.
5. Save assessment evidence.
6. Apply structured state updates through `StateUpdater`.

# Goals

- Add an assessment workflow for the current lesson.
- Add a CLI command shaped as `learn assess --response <path>`.
- Load the current curriculum and state using existing loaders.
- Load the latest teaching output from `MemoryStore`.
- Read the learner response from a file.
- Save the learner response to `MemoryStore`.
- Build an assessment prompt.
- Call the configured LLM through the existing LLM boundary.
- Save assessment output to `MemoryStore`.
- Apply the returned `state_update` through `StateUpdater`.
- Ensure progress is based on learner evidence, not teaching output alone.

# Non-goals

- Do not add a planner.
- Do not add progression policy beyond assessment prompt rules.
- Do not modify the curriculum format.
- Do not change `StateUpdater` responsibilities.
- Do not change the state schema unless a separate accepted RFC requires it.
- Do not add embeddings, vector search, RAG, or semantic memory.
- Do not add a web UI.
- Do not add a database server.
- Do not add a session manager.
- Do not rewrite `MemoryStore`.

# Current State

The current CLI has one primary flow:

1. Load state from `state/navigation.yaml`.
2. Resolve the current lesson.
3. Load curriculum index, phase index, current lesson, phase progress, review queue, and optional notes.
4. Build a teaching prompt.
5. Call the LLM.
6. Print teaching output.
7. Ask the LLM for a structured state update.
8. Apply the update through `StateUpdater`.

The current prompt builder has teaching and state-update prompt functions. The state updater expects JSON and writes navigation, progress, review queue, and lesson notes.

There is no assessment command. There is also no current workflow for reading learner responses from disk or saving learner responses and assessment outputs as raw evidence.

# Proposed Design

Add a learner assessment workflow as a separate CLI path from teaching.

The assessment workflow should reuse existing components:

- `CurriculumLoader` for current lesson context.
- `StateLoader` for current learning state.
- `MemoryStore` for teaching output, learner response, and assessment output.
- `PromptBuilder` for assessment prompt construction.
- `LLMClient` for model calls.
- `StateUpdater` for state changes.

Add a prompt-builder function:

```text
build_assessment_prompt(context, teaching_output, learner_response)
```

The assessment prompt should include only necessary context:

- current curriculum context
- current state context
- latest teaching output
- learner response
- current lesson goal

The expected LLM output should be JSON only and include:

- `assessment`
- `state_update`

The CLI interaction should be:

```text
learn assess --response responses/today.md
```

Workflow responsibilities:

1. CLI parses the assessment command and response path.
2. Existing loaders build the current learning context.
3. `MemoryStore.latest(lesson_id, "teaching")` retrieves the latest teaching output.
4. CLI reads the learner response file.
5. CLI saves the learner response as a memory record.
6. Prompt builder builds the assessment prompt.
7. LLM client generates assessment JSON.
8. CLI saves the raw assessment output as a memory record.
9. `StateUpdater` applies the `state_update`.

Boundary rules:

- `MemoryStore` stores evidence but does not update state.
- `StateUpdater` updates state but does not write memory.
- The LLM returns structured data but never writes files directly.
- The assessment workflow evaluates learner evidence, not teaching quality.

# Alternatives Considered

Alternative 1: Continue updating state after teaching output only

- Advantages:
  - No new command.
  - No learner-response workflow.
  - Keeps the current CLI simple.
- Disadvantages:
  - Progress may be inferred without learner evidence.
  - Weak basis for marking topics complete.
  - Does not support assessment-specific feedback.
- Decision:
  - Not selected. The issue explicitly requires learner evidence before assessment-driven state updates.

Alternative 2: Add interactive assessment through stdin

- Advantages:
  - Convenient for quick local use.
  - Avoids managing response files.
  - Feels conversational.
- Disadvantages:
  - Harder to reproduce and audit.
  - Harder to persist the exact learner response before assessment.
  - More complex terminal UX.
- Decision:
  - Not selected for the first version. File input is simpler, testable, and auditable.

Alternative 3: Combine teaching and assessment into one command

- Advantages:
  - One user-facing command.
  - Could feel like a complete learning session.
  - Avoids command branching.
- Disadvantages:
  - Blurs teaching and assessment responsibilities.
  - Requires interactive response collection or implicit learner evidence.
  - Makes it harder to persist and inspect each step independently.
- Decision:
  - Not selected. Separate `teach` and `assess` steps are clearer and match the evidence-first workflow.

Alternative 4: Build a rule-based assessor without an LLM

- Advantages:
  - Deterministic.
  - Lower model cost.
  - Easier to test for simple checks.
- Disadvantages:
  - Poor fit for open-ended learner explanations.
  - Requires hand-authored rubrics that do not exist yet.
  - Likely duplicates curriculum interpretation logic.
- Decision:
  - Not selected. The LLM is already part of the architecture and can evaluate open-ended responses with structured output constraints.

# Trade-offs

The proposed workflow adds a second command and a second prompt type. That increases the CLI surface area, but it keeps teaching and assessment responsibilities separate.

Saving learner responses and assessment outputs creates more local files. This improves auditability and reproducibility at the cost of managing a `memory/` directory.

The assessment remains probabilistic because it relies on an LLM. The structured prompt and `StateUpdater` boundary reduce risk, but they do not make assessment fully deterministic.

The first version intentionally avoids an advanced progression policy. That keeps implementation small, but it leaves some promotion and mastery rules for later review.

# Open Questions

- What exact `record_type` names should be used for learner responses and assessments?
- Should assessment output be parsed before saving, or saved exactly as returned by the LLM?
- Should the assessment command fail if no teaching output exists, or continue with a warning?
- What minimum evidence is required before marking a topic completed?
- Should the learner response file be copied into memory verbatim or normalized?
- Should assessment feedback be printed to the terminal in addition to being saved?

