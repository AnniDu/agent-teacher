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

The CLI reads `state/navigation.yaml`, loads only the current phase and lesson from `curriculum/`, asks the configured LLM to teach the lesson, saves the teaching output to `memory/<lesson_id>/teaching.json`, then asks for a structured JSON state update. The LLM never writes files directly; Python code owns all persistence.

`memory/` stores raw learning evidence, such as teaching output returned by the LLM. `state/` stores mutable learner state derived from workflows, such as navigation, progress, review queues, and lesson notes. `MemoryStore` writes memory records only; `StateUpdater` applies state updates only.

## Current Scope

Implemented:

- file-based curriculum loading
- file-based learning state loading
- compact teaching prompt construction
- provider-neutral LLM interface
- Gemini-backed LLM client
- structured JSON state update parsing
- YAML and Markdown state writes
- JSON memory writes for teaching output
- `learn` CLI entry point

Not implemented yet:

- multi-agent orchestration
- vector search or RAG
- semantic memory
- scheduling
- web UI
- database storage
- authentication or user accounts
- LangGraph, MCP, or framework-specific workflows
