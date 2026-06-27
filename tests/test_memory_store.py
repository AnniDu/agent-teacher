from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent_teacher.memory_store import JsonMemoryStore, MemoryRecord, MemoryStoreError


class JsonMemoryStoreTest(unittest.TestCase):
    def test_save_writes_record_to_lesson_record_type_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            store = JsonMemoryStore(repo_root)
            record = _record()

            store.save(record)

            path = repo_root / "memory" / "P0L1" / "teaching.json"
            self.assertTrue(path.exists())
            data = json.loads(path.read_text())
            self.assertEqual(data["record_id"], "record-1")
            self.assertEqual(data["lesson_id"], "P0L1")
            self.assertEqual(data["record_type"], "teaching")
            self.assertEqual(data["content"], "Lesson output")
            self.assertEqual(data["metadata"], {"phase": "P0"})
            self.assertEqual(data["created_at"], "2026-06-27T00:00:00Z")

    def test_get_loads_record_by_record_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = JsonMemoryStore(Path(tmpdir))
            record = _record()
            store.save(record)

            loaded = store.get("record-1")

            self.assertEqual(loaded, record)

    def test_latest_loads_record_for_lesson_and_record_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = JsonMemoryStore(Path(tmpdir))
            record = _record()
            store.save(record)

            latest = store.latest("P0L1", "teaching")

            self.assertEqual(latest, record)

    def test_invalid_path_segments_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = JsonMemoryStore(Path(tmpdir))

            with self.assertRaises(MemoryStoreError):
                store.save(_record(lesson_id="P0/L1"))

            with self.assertRaises(MemoryStoreError):
                store.save(_record(record_type="teach/ing"))


def _record(lesson_id: str = "P0L1", record_type: str = "teaching") -> MemoryRecord:
    return MemoryRecord(
        record_id="record-1",
        lesson_id=lesson_id,
        record_type=record_type,
        content="Lesson output",
        metadata={"phase": "P0"},
        created_at="2026-06-27T00:00:00Z",
    )


if __name__ == "__main__":
    unittest.main()
