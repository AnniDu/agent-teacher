from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from agent_teacher import cli
from agent_teacher.models import CurriculumContext, LearningContext, StateContext


class CliTeachingMemoryTest(unittest.TestCase):
    def test_learn_persists_teaching_output_to_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            context = _context(repo_root)
            llm = Mock()
            llm.generate.side_effect = ["Teaching output", '{"state_update": {}}']

            with (
                patch("agent_teacher.cli._load_context", return_value=context),
                patch("agent_teacher.cli.default_llm_client", return_value=llm),
                patch("agent_teacher.cli.StateUpdater") as state_updater,
                redirect_stdout(StringIO()),
            ):
                result = cli.main(["--repo-root", str(repo_root)])

            self.assertEqual(result, 0)
            record_path = repo_root / "memory" / "P0L1" / "teaching.json"
            self.assertTrue(record_path.exists())
            record = json.loads(record_path.read_text())
            self.assertEqual(record["record_id"], "P0L1-teaching")
            self.assertEqual(record["lesson_id"], "P0L1")
            self.assertEqual(record["record_type"], "teaching")
            self.assertEqual(record["content"], "Teaching output")
            self.assertEqual(
                record["metadata"],
                {
                    "phase": "P0",
                    "lesson_id": "P0L1",
                    "lesson_path": "curriculum/phase0/lesson01-representation-learning-foundations.md",
                },
            )
            self.assertTrue(record["created_at"].endswith("Z"))
            state_updater.return_value.apply.assert_called_once()

    def test_learn_teach_runs_teaching_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            llm = Mock()
            llm.generate.side_effect = ["Teaching output", '{"state_update": {}}']

            with (
                patch("agent_teacher.cli._load_context", return_value=_context(repo_root)),
                patch("agent_teacher.cli.default_llm_client", return_value=llm),
                patch("agent_teacher.cli.StateUpdater"),
                redirect_stdout(StringIO()),
            ):
                result = cli.main(["teach", "--repo-root", str(repo_root)])

            self.assertEqual(result, 0)
            self.assertTrue((repo_root / "memory" / "P0L1" / "teaching.json").exists())
            self.assertEqual(llm.generate.call_count, 2)


def _context(repo_root: Path) -> LearningContext:
    lesson_path = repo_root / "curriculum" / "phase0" / "lesson01-representation-learning-foundations.md"
    return LearningContext(
        curriculum=CurriculumContext(
            course_index="Course index",
            phase_index="Phase index",
            lesson="Lesson",
            phase_id="P0",
            lesson_id="P0L1",
            previous_lesson_id=None,
            lesson_path=lesson_path,
        ),
        state=StateContext(
            navigation={"current": {"phase": "P0", "lesson": "P0L1", "topic": None}},
            progress={},
            review_queue={"queue": []},
            lesson_note=None,
            previous_lesson_note=None,
            lesson_note_path=repo_root / "state" / "lesson_notes" / "P0L1.md",
        ),
    )


if __name__ == "__main__":
    unittest.main()
