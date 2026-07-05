from __future__ import annotations

import unittest
from pathlib import Path

from backend.curriculum.curriculum_loader import CurriculumLoader


class CurriculumLoaderTest(unittest.TestCase):
    def test_loads_existing_lab_curriculum(self) -> None:
        curriculum = CurriculumLoader(Path("curriculum")).load()

        lesson = curriculum.default_lesson()

        self.assertEqual(lesson.lesson_id, "P0L1")
        self.assertEqual(lesson.phase_id, "P0")
        self.assertEqual(curriculum.first_topic("P0L1"), "Scalar, Vector, Matrix, Tensor")
        self.assertEqual(
            curriculum.next_topic("P0L1", "Scalar, Vector, Matrix, Tensor"),
            "Vector Space Intuition",
        )
        self.assertIn(
            "Scalar, Vector, Matrix, Tensor",
            curriculum.content_for("P0L1", "Scalar, Vector, Matrix, Tensor"),
        )


if __name__ == "__main__":
    unittest.main()
