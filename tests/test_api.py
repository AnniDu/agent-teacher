from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import create_app


class ApiTest(unittest.TestCase):
    def test_serves_frontend_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            client = _client(Path(tmpdir), _FakeLlm([]), serve_frontend=True)

            response = client.get("/")

            self.assertEqual(response.status_code, 200)
            self.assertIn("Learning Coach", response.text)
            self.assertIn("/app.js", response.text)

    def test_serves_frontend_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            client = _client(Path(tmpdir), _FakeLlm([]), serve_frontend=True)

            response = client.get("/app.js")

            self.assertEqual(response.status_code, 200)
            self.assertIn('requestJson("/chat"', response.text)

    def test_get_state_returns_initial_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            client = _client(Path(tmpdir), _FakeLlm([]))

            response = client.get("/state/student-1")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["current_lesson"], "P0L1")
            self.assertEqual(response.json()["current_mode"], "teach")

    def test_reset_state_persists_requested_location(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            client = _client(Path(tmpdir), _FakeLlm([]))

            response = client.post(
                "/state/student-1/reset",
                json={"phase": "P1", "lesson": "P1LAB1", "topic": "Teaching Workflow"},
            )
            state_response = client.get("/state/student-1")

            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()["ok"])
            self.assertEqual(state_response.json()["current_topic"], "Teaching Workflow")

    def test_chat_runs_learning_loop_and_saves_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            client = _client(root, _FakeLlm([_teaching_response()]))

            response = client.post("/chat", json={"student_id": "student-1", "message": "start"})
            state_response = client.get("/state/student-1")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.json().keys()), {"message", "state"})
            self.assertIn("Learning state tracks progress.", response.json()["message"])
            self.assertEqual(response.json()["state"]["current_mode"], "assess")
            self.assertEqual(state_response.json()["current_mode"], "assess")
            self.assertTrue((root / "data" / "events" / "student-1.jsonl").exists())


class _FakeLlm:
    def __init__(self, responses: list) -> None:
        self.responses = responses

    def generate(self, prompt: str) -> str:
        return self.responses.pop(0)


def _client(root: Path, llm: _FakeLlm, serve_frontend: bool = False) -> TestClient:
    repo_root = Path.cwd() if serve_frontend else root
    with patch.dict(
        "os.environ",
        {
            "LEARNING_COACH_DATA_DIR": str(root / "data"),
            "LEARNING_COACH_CURRICULUM_DIR": str(Path("curriculum").resolve()),
        },
    ):
        return TestClient(create_app(repo_root=repo_root, llm_client=llm))


def _teaching_response() -> str:
    return json.dumps(
        {
            "explanation": "Learning state tracks progress.",
            "question": "What is learning state?",
        }
    )


if __name__ == "__main__":
    unittest.main()
