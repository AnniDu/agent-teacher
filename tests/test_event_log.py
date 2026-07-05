from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from backend.events.event_log import EventLog


class EventLogTest(unittest.TestCase):
    def test_appends_jsonl_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            event_log = EventLog(Path(tmpdir))

            event_log.append("student-1", "student_message", {"message": "hello"})
            event_log.append("student-1", "assistant_message", {"message": "hi"})

            lines = (Path(tmpdir) / "events" / "student-1.jsonl").read_text().splitlines()
            events = [json.loads(line) for line in lines]
            self.assertEqual([event["type"] for event in events], ["student_message", "assistant_message"])
            self.assertEqual(events[0]["student_id"], "student-1")
            self.assertIn("created_at", events[0])


if __name__ == "__main__":
    unittest.main()
