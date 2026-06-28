# Status

Draft

# Problem

The assessment workflow reads a learner response from a file, but the CLI does not provide a way to create that response file.

Users must manually create response files outside the tool before running `learn assess --response <path>`. That leaves a gap in the intended teach to respond to assess workflow and makes the learner response capture step less consistent and less discoverable.

# Motivation

The project now has explicit teaching and assessment commands:

```text
learn teach
learn assess --response responses/today.md
```

Assessment is evidence-based, but the evidence file is currently created out of band. A small response capture command would keep the workflow inside the CLI while still preserving the assessment command's file-based, auditable input.

This should be a narrow utility command. It should write a response file only; assessment and memory persistence remain separate workflow responsibilities.

# Goals

- Add a learner response capture command:

```text
learn respond --output responses/today.md
```

- Read learner response text from standard input.
- Require non-empty input after trimming surrounding whitespace.
- Resolve relative output paths under the repository root.
- Create parent directories for the output path when needed.
- Write the response text to the output path.
- Print the saved path.
- Ensure `learn assess --response responses/today.md` can read the generated file.

# Non-goals

- Do not run assessment.
- Do not write to `MemoryStore` from the response capture command.
- Do not add interactive editor support.
- Do not add a UI or API layer.
- Do not change the state schema.
- Do not change assessment prompt behavior.
- Do not change `StateUpdater` responsibilities.

# Current State

The current CLI behaves as a command group:

```text
learn
learn teach
learn assess --response responses/today.md
```

`learn` prints usage.

`learn teach` teaches the current lesson, saves teaching output to `MemoryStore`, and applies a teaching state update through `StateUpdater`.

`learn assess --response <path>` reads a learner response file, loads latest teaching output from `MemoryStore`, saves learner response and assessment output to `MemoryStore`, and applies the returned `state_update` through `StateUpdater`.

There is no command for creating the response file consumed by assessment.

# Proposed Design

Add a third explicit CLI workflow:

```text
learn respond --output responses/today.md
```

The response capture workflow should:

1. Parse the `respond` command and required `--output <path>`.
2. Resolve the output path:
   - absolute paths are used as provided
   - relative paths are resolved under the repository root
3. Read all text from `stdin`.
4. Reject empty input after trimming surrounding whitespace.
5. Create the output path's parent directories.
6. Write the learner response text to the output path.
7. Print the saved path.

The response capture command should not load curriculum state, call the LLM, update `state/`, or write `memory/`.

Module responsibilities:

- CLI
  - Owns command parsing and response file writing.
  - Resolves repository-relative output paths.
  - Does not run assessment from `respond`.

- `MemoryStore`
  - Remains responsible for raw evidence records written by teaching and assessment workflows.
  - Is not used by `respond`.

- `StateUpdater`
  - Remains responsible only for applying structured state updates.
  - Is not used by `respond`.

# Alternatives Considered

Alternative 1: Keep manual file creation outside the CLI

- Advantages:
  - No new command.
  - No file-writing logic in the CLI.
- Disadvantages:
  - Leaves a gap in the documented workflow.
  - Makes the response path less discoverable.
  - Gives users inconsistent behavior across teach, respond, and assess steps.
- Decision:
  - Not selected. The issue explicitly asks for CLI response capture.

Alternative 2: Let `learn assess` read from stdin directly

- Advantages:
  - Fewer commands.
  - Convenient one-step assessment.
- Disadvantages:
  - Less auditable because the response file may not exist before assessment.
  - Blurs response capture and assessment responsibilities.
  - Makes it harder to rerun assessment against the same response.
- Decision:
  - Not selected. `learn assess --response <path>` should continue to read an explicit file.

Alternative 3: Save response directly to `MemoryStore` from `learn respond`

- Advantages:
  - Captures evidence immediately.
  - Avoids a later assessment write for learner response.
- Disadvantages:
  - Expands `respond` beyond file capture.
  - Creates memory records without assessment context.
  - Conflicts with the issue non-goal to avoid direct `MemoryStore` writes.
- Decision:
  - Not selected. `respond` should only create the response file.

Alternative 4: Add interactive editor support

- Advantages:
  - Better editing experience for long responses.
- Disadvantages:
  - Requires editor process handling and cross-platform terminal behavior.
  - Larger UX surface than this issue requires.
- Decision:
  - Not selected. Standard input is sufficient for the first version.

# Trade-offs

Adding `learn respond` introduces another CLI command, but the command is narrow and completes the teach to respond to assess workflow without changing assessment semantics.

Reading from `stdin` is simple and scriptable, but it is less ergonomic for long-form writing than an editor. The generated file remains easy to inspect and reuse.

Writing a plain response file instead of memory keeps workflow boundaries clear. The assessment workflow remains the place where learner response evidence enters `MemoryStore`.

# Open Questions

- Should `learn respond` preserve trailing newlines exactly as entered or normalize to a single trailing newline?
- Should overwriting an existing response file require an explicit flag?
- Should the saved path be printed as absolute or repository-relative?
- Should future response capture support an editor mode?
