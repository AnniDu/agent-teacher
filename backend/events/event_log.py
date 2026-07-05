from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from backend.state.models import utc_now


class EventLog:
    def __init__(self, data_dir: Path) -> None:
        self._events_dir = data_dir / "events"

    def append(self, student_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        path = self._events_dir / f"{student_id}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "type": event_type,
            "student_id": student_id,
            "created_at": utc_now(),
            **payload,
        }
        with path.open("a") as file:
            file.write(json.dumps(record, sort_keys=True) + "\n")
