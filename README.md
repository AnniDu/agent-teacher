# Agent Teacher

CLI Learning Agent for the modular AI Systems Engineering curriculum.

## Setup

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
```

Set the environment variables in `.env` or export them in your shell:

```bash
export GEMINI_API_KEY="your-api-key"
export GEMINI_MODEL="gemini-1.5-flash"
```

## Run

```bash
learn
```

You can also run the teaching workflow explicitly:

```bash
learn teach
```

The CLI reads `state/navigation.yaml`, loads only the current phase and lesson from `curriculum/`, asks the configured LLM to teach the lesson, saves that teaching output under `memory/<lesson_id>/teaching.json`, then asks for a structured JSON state update. The LLM never writes files directly; the Python state updater applies the structured update to files under `state/`.

## State and Memory

`state/` contains derived learner state used to continue the curriculum flow, including navigation, progress, review queue items, and lesson notes.

`memory/` contains raw learning evidence from interactions. Teaching output is stored as a JSON memory record at `memory/<lesson_id>/teaching.json` with record metadata such as phase, lesson id, and lesson path.

`StateUpdater` writes only `state/` files. `MemoryStore` writes only raw evidence under `memory/` and does not update learner state.

## Current Scope

Implemented:

- file-based curriculum loading
- file-based learning state loading
- compact teaching prompt construction
- provider-neutral LLM interface
- Gemini-backed LLM client
- structured JSON state update parsing
- YAML and Markdown state writes
- JSON-backed memory records
- `learn` CLI entry point

Not implemented yet:

- learner responses
- learner assessment
- multi-agent orchestration
- vector search or RAG
- semantic memory
- scheduling
- web UI
- database storage
- authentication or user accounts
- LangGraph, MCP, or framework-specific workflows
