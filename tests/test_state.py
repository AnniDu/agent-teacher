from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from backend.curriculum.curriculum_loader import CurriculumLoader
from backend.state.state_manager import StateManager
from backend.state.state_store import FileStateStore


class StateManagerTest(unittest.TestCase):
    def test_persists_learning_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            curriculum = CurriculumLoader(Path("curriculum")).load()
            manager = StateManager(FileStateStore(Path(tmpdir)), curriculum)
            state = manager.initial_state("student-1")
            state.current_mode = "assess"
            state.last_question = "What is learning state?"

            manager.save(state)
            loaded = manager.load("student-1")

            self.assertEqual(loaded.current_lesson, "P0L1")
            self.assertEqual(loaded.current_topic, "Scalar, Vector, Matrix, Tensor")
            self.assertEqual(loaded.current_mode, "assess")
            self.assertEqual(loaded.last_question, "What is learning state?")


if __name__ == "__main__":
    unittest.main()
