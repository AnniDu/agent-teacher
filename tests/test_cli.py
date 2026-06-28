from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from agent_teacher import cli
from agent_teacher.memory_store import JsonMemoryStore, MemoryRecord


class CliTest(unittest.TestCase):
    def test_learn_persists_teaching_output_to_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = _write_repo_fixture(Path(tmpdir))

            exit_code = _run_cli(repo_root)

            self.assertEqual(exit_code, 0)
            _assert_teaching_memory(self, repo_root)

    def test_learn_teach_persists_teaching_output_to_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = _write_repo_fixture(Path(tmpdir))

            exit_code = _run_cli(repo_root, "teach")

            self.assertEqual(exit_code, 0)
            _assert_teaching_memory(self, repo_root)

    def test_assess_saves_response_assessment_and_updates_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = _write_repo_fixture(Path(tmpdir))
            fake_llm = _FakeLlm([_assessment_response()])
            _write_teaching_memory(repo_root)
            response_path = repo_root / "responses" / "today.md"
            response_path.parent.mkdir()
            response_path.write_text("I think vectors encode meaning by position.")

            exit_code = _run_cli(
                repo_root,
                "assess",
                "--response",
                "responses/today.md",
                llm=fake_llm,
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(len(fake_llm.prompts), 1)
            self.assertIn("Teaching output from memory", fake_llm.prompts[0])
            self.assertIn("I think vectors encode meaning by position.", fake_llm.prompts[0])
            learner_response = json.loads(
                (repo_root / "memory" / "P0L1" / "learner_response.json").read_text()
            )
            assessment = json.loads(
                (repo_root / "memory" / "P0L1" / "assessment.json").read_text()
            )
            progress = (repo_root / "state" / "progress" / "phase0.yaml").read_text()
            self.assertEqual(
                learner_response["content"], "I think vectors encode meaning by position."
            )
            self.assertEqual(learner_response["record_type"], "learner_response")
            self.assertEqual(learner_response["metadata"]["response_path"], str(response_path))
            self.assertIn('"assessment"', assessment["content"])
            self.assertEqual(assessment["record_type"], "assessment")
            self.assertIn("status: in_progress", progress)


class _FakeLlm:
    def __init__(self, responses: list[str] | None = None) -> None:
        self.responses = responses or ["Teaching output", '{"state_update": {}}']
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def _run_cli(repo_root: Path, *args: str, llm: _FakeLlm | None = None) -> int:
    argv = ["--repo-root", str(repo_root), *args]
    fake_llm = llm or _FakeLlm()
    with (
        patch("agent_teacher.cli.default_llm_client", return_value=fake_llm),
        patch("agent_teacher.cli._utc_now", return_value="2026-06-27T00:00:00Z"),
        redirect_stdout(io.StringIO()),
    ):
        return cli.main(argv)


def _assert_teaching_memory(test: unittest.TestCase, repo_root: Path) -> None:
    path = repo_root / "memory" / "P0L1" / "teaching.json"
    test.assertTrue(path.exists())
    data = json.loads(path.read_text())
    test.assertEqual(data["record_id"], "P0L1:teaching")
    test.assertEqual(data["lesson_id"], "P0L1")
    test.assertEqual(data["record_type"], "teaching")
    test.assertEqual(data["content"], "Teaching output")
    test.assertEqual(
        data["metadata"],
        {
            "phase": "P0",
            "lesson_id": "P0L1",
            "lesson_path": str(repo_root / "curriculum" / "phase0" / "lesson01-intro.md"),
        },
    )
    test.assertEqual(data["created_at"], "2026-06-27T00:00:00Z")


def _write_teaching_memory(repo_root: Path) -> None:
    JsonMemoryStore(repo_root).save(
        MemoryRecord(
            record_id="P0L1:teaching",
            lesson_id="P0L1",
            record_type="teaching",
            content="Teaching output from memory",
            metadata={"phase": "P0", "lesson_id": "P0L1"},
            created_at="2026-06-27T00:00:00Z",
        )
    )


def _assessment_response() -> str:
    return json.dumps(
        {
            "assessment": {
                "lesson_id": "P0L1",
                "summary": "Partial understanding",
                "evidence": ["Learner mentioned vectors and meaning"],
                "gaps": [],
                "feedback": "Keep practicing.",
            },
            "state_update": {
                "progress": {
                    "phase": "P0",
                    "lesson_id": "P0L1",
                    "status": "in_progress",
                    "completed_topics": ["Vector Space Intuition"],
                }
            },
        }
    )


def _write_repo_fixture(repo_root: Path) -> Path:
    repo_root = repo_root.resolve()
    (repo_root / "curriculum" / "phase0").mkdir(parents=True)
    (repo_root / "state" / "progress").mkdir(parents=True)

    (repo_root / "curriculum" / "index.md").write_text("# Course\n")
    (repo_root / "curriculum" / "phase0" / "index.md").write_text(
        "# Phase 0\n\n1. [Intro](lesson01-intro.md)\n"
    )
    (repo_root / "curriculum" / "phase0" / "lesson01-intro.md").write_text(
        "---\nprevious: null\n---\n# Intro\n"
    )
    (repo_root / "state" / "navigation.yaml").write_text(
        "current:\n  phase: P0\n  lesson: P0L1\n  topic: null\n"
    )
    (repo_root / "state" / "progress" / "phase0.yaml").write_text(
        "phase: P0\nlessons:\n  - lesson_id: P0L1\n    status: not_started\n"
    )
    (repo_root / "state" / "review_queue.yaml").write_text("queue: []\n")
    return repo_root


if __name__ == "__main__":
    unittest.main()
