# Agent Teacher

Backend MVP for the Lab 1 Learning Coach Agent.

The backend implements an explicit learning loop:

1. Load persisted learning state.
2. Determine workflow mode from backend state.
3. Call the LLM only for bounded reasoning tasks.
4. Apply deterministic state transitions in code.
5. Persist state and append development events.

The frontend is intentionally out of scope for Lab 1.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install '.[test]'
```

Configure Gemini through environment variables:

```bash
export GEMINI_API_KEY="your-api-key"
export GEMINI_MODEL="gemini-1.5-flash"
```

Or put the values in a local `.env` file:

```bash
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-1.5-flash
```

`.env` is ignored by Git and must not be committed.

`GEMINI_MODEL` defaults to `gemini-1.5-flash` if unset.

## Run

```bash
uvicorn backend.app:app --reload
```

## API

```text
POST /chat
GET /state/{student_id}
POST /state/{student_id}/reset
```

State is stored under `data/students/{student_id}/state.json`.

Development events are appended to `data/events/{student_id}.jsonl`.

## Test

```bash
PYTHONPATH=. python -m unittest discover -s tests
```
