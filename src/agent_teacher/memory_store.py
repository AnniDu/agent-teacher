from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class MemoryStoreError(RuntimeError):
    pass


@dataclass(frozen=True)
class MemoryRecord:
    record_id: str
    lesson_id: str
    record_type: str
    content: str
    metadata: dict[str, Any]
    created_at: str


class MemoryStore(ABC):
    @abstractmethod
    def save(self, record: MemoryRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, record_id: str) -> MemoryRecord | None:
        raise NotImplementedError

    @abstractmethod
    def latest(self, lesson_id: str, record_type: str) -> MemoryRecord | None:
        raise NotImplementedError


class JsonMemoryStore(MemoryStore):
    def __init__(self, repo_root: Path) -> None:
        self.memory_dir = repo_root / "memory"

    def save(self, record: MemoryRecord) -> None:
        self._validate_record(record)
        path = self._record_path(record.lesson_id, record.record_type)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(record), indent=2, sort_keys=True) + "\n")

    def get(self, record_id: str) -> MemoryRecord | None:
        for path in self.memory_dir.glob("*/*.json"):
            record = self._load_record(path)
            if record.record_id == record_id:
                return record
        return None

    def latest(self, lesson_id: str, record_type: str) -> MemoryRecord | None:
        path = self._record_path(lesson_id, record_type)
        if not path.exists():
            return None
        return self._load_record(path)

    def _record_path(self, lesson_id: str, record_type: str) -> Path:
        _validate_path_segment("lesson_id", lesson_id)
        _validate_path_segment("record_type", record_type)
        return self.memory_dir / lesson_id / f"{record_type}.json"

    def _load_record(self, path: Path) -> MemoryRecord:
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise MemoryStoreError(f"Invalid memory record JSON: {path}") from exc
        if not isinstance(data, dict):
            raise MemoryStoreError(f"Memory record must be a JSON object: {path}")
        return _record_from_dict(data, path)

    def _validate_record(self, record: MemoryRecord) -> None:
        _validate_path_segment("lesson_id", record.lesson_id)
        _validate_path_segment("record_type", record.record_type)
        if not record.record_id:
            raise MemoryStoreError("record_id is required")
        if not record.created_at:
            raise MemoryStoreError("created_at is required")


def _record_from_dict(data: dict[str, Any], path: Path) -> MemoryRecord:
    required_fields = ("record_id", "lesson_id", "record_type", "content", "metadata", "created_at")
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise MemoryStoreError(f"Memory record {path} is missing fields: {', '.join(missing)}")
    if not isinstance(data["metadata"], dict):
        raise MemoryStoreError(f"Memory record metadata must be an object: {path}")
    return MemoryRecord(
        record_id=str(data["record_id"]),
        lesson_id=str(data["lesson_id"]),
        record_type=str(data["record_type"]),
        content=str(data["content"]),
        metadata=data["metadata"],
        created_at=str(data["created_at"]),
    )


def _validate_path_segment(field_name: str, value: str) -> None:
    if not value or "/" in value or "\\" in value or value in {".", ".."}:
        raise MemoryStoreError(f"{field_name} must be a simple path segment")

