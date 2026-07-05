from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import LearningState


class FileStateStore:
    def __init__(self, data_dir: Path) -> None:
        self._students_dir = data_dir / "students"

    def load(self, student_id: str) -> Optional[LearningState]:
        path = self._path(student_id)
        if not path.exists():
            return None
        return LearningState.from_dict(json.loads(path.read_text()))

    def save(self, state: LearningState) -> None:
        path = self._path(state.student_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n")

    def _path(self, student_id: str) -> Path:
        return self._students_dir / student_id / "state.json"
