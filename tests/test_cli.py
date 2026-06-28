from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from agent_teacher import cli


class CliTest(unittest.TestCase):
    def test_learn_persists_teaching_output_to_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = _write_repo_fixture(Path(tmpdir))

            exit_code = _run_cli(repo_root)

            self.assertEqual(exit_code, 0)
            _assert_teaching_memory(self, repo_root)


class _FakeLlm:
    def __init__(self) -> None:
        self.responses = ["Teaching output", '{"state_update": {}}']

    def generate(self, prompt: str) -> str:
        return self.responses.pop(0)


def _run_cli(repo_root: Path) -> int:
    argv = ["--repo-root", str(repo_root)]
    with (
        patch("agent_teacher.cli.default_llm_client", return_value=_FakeLlm()),
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
