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
- Preserve the learner response content as entered while ensuring exactly one trailing newline.
- Fail with a clear error if the output file already exists.
- Print the saved path as repository-relative when it is under the repository root, otherwise print the absolute path.
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
3. Fail with a clear error if the output file already exists.
4. Read all text from `stdin`.
5. Use `input.strip()` only to determine whether the response is empty.
6. Reject the response if `input.strip()` is empty.
7. Create the output path's parent directories.
8. Write the original input exactly as received, except ensure the saved file has exactly one trailing newline.
9. Print the saved path:
   - repository-relative when the output path is under the repository root
   - absolute when the output path is outside the repository root

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
  - Not selected. `learn respond` should remain a narrow standard-input capture utility. Future editor integration should be proposed separately if needed.

# Trade-offs

Adding `learn respond` introduces another CLI command, but the command is narrow and completes the teach to respond to assess workflow without changing assessment semantics.

Reading from `stdin` is simple and scriptable, but it is less ergonomic for long-form writing than an editor. The generated file remains easy to inspect and reuse.

Preserving response text avoids silently transforming learner content. Ensuring exactly one trailing newline keeps generated files conventional and predictable without changing the substantive response.

Failing when the output file already exists prevents accidental response loss. A future `--force` flag can add explicit overwrite behavior if needed.

Printing repository-relative paths for files under the repo keeps normal workflow output concise while still supporting absolute paths outside the repo.

Writing a plain response file instead of memory keeps workflow boundaries clear. The assessment workflow remains the place where learner response evidence enters `MemoryStore`.
