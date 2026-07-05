from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Optional

from backend.config import load_settings
from backend.core.learning_loop import LearningLoop
from backend.curriculum.curriculum_loader import CurriculumLoader
from backend.events.event_log import EventLog
from backend.services.assessment_service import AssessmentService
from backend.services.teaching_service import TeachingService
from backend.state.state_manager import StateManager
from backend.state.state_store import FileStateStore


class LearningLoopTest(unittest.TestCase):
    def test_teach_to_assess_transition(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            components = _components(Path(tmpdir), _FakeLlm([_teaching_response()]))
            state = components.state_manager.initial_state("student-1")

            result = components.learning_loop.run(state, "")

            self.assertEqual(result.state.current_mode, "assess")
            self.assertEqual(result.state.next_step, "wait_for_answer")
            self.assertEqual(result.state.last_question, "What is learning state?")
            self.assertIn("Learning state tracks progress.", result.message)

    def test_assessment_with_high_score_moves_to_next_topic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            components = _components(Path(tmpdir), _FakeLlm([_assessment_response(0.9)]))
            state = components.state_manager.initial_state("student-1")
            state.current_mode = "assess"
            state.last_question = "What is learning state?"

            result = components.learning_loop.run(state, "State tracks where the learner is.")

            self.assertEqual(result.state.current_mode, "teach")
            self.assertEqual(result.state.current_topic, "Vector Space Intuition")
            self.assertEqual(result.state.next_step, "teach_next_topic")
            self.assertIn("Scalar, Vector, Matrix, Tensor", result.state.completed_topics)
            self.assertEqual(result.state.understanding_score, 0.9)

    def test_assessment_with_low_score_reteaches_current_topic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            components = _components(
                Path(tmpdir),
                _FakeLlm([_assessment_response(0.4, misconceptions=["State is memory"])]),
            )
            state = components.state_manager.initial_state("student-1")
            state.current_mode = "assess"
            state.last_question = "What is learning state?"

            result = components.learning_loop.run(state, "It stores every memory forever.")

            self.assertEqual(result.state.current_mode, "teach")
            self.assertEqual(result.state.current_topic, "Scalar, Vector, Matrix, Tensor")
            self.assertEqual(result.state.next_step, "reteach_current_topic")
            self.assertEqual(result.state.misconceptions, ["State is memory"])

    def test_loop_writes_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            components = _components(root, _FakeLlm([_teaching_response()]))
            state = components.state_manager.initial_state("student-1")

            components.learning_loop.run(state, "")

            lines = (root / "data" / "events" / "student-1.jsonl").read_text().splitlines()
            event_types = [json.loads(line)["type"] for line in lines]
            self.assertEqual(
                event_types,
                ["student_message", "state_transition", "assistant_message"],
            )


class _Components:
    def __init__(self, state_manager: StateManager, learning_loop: LearningLoop) -> None:
        self.state_manager = state_manager
        self.learning_loop = learning_loop


class _FakeLlm:
    def __init__(self, responses: list) -> None:
        self.responses = responses
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def _components(root: Path, llm: _FakeLlm) -> _Components:
    settings = load_settings(root)
    curriculum = CurriculumLoader(Path("curriculum")).load()
    state_manager = StateManager(FileStateStore(settings.data_dir), curriculum)
    learning_loop = LearningLoop(
        curriculum=curriculum,
        teaching_service=TeachingService(llm),
        assessment_service=AssessmentService(llm),
        event_log=EventLog(settings.data_dir),
        settings=settings,
    )
    return _Components(state_manager, learning_loop)


def _teaching_response() -> str:
    return json.dumps(
        {
            "explanation": "Learning state tracks progress.",
            "question": "What is learning state?",
        }
    )


def _assessment_response(score: float, misconceptions: Optional[list] = None) -> str:
    return json.dumps(
        {
            "score": score,
            "feedback": "Assessment feedback.",
            "misconceptions": misconceptions or [],
        }
    )


if __name__ == "__main__":
    unittest.main()
