from __future__ import annotations

import unittest
from pathlib import Path

from backend.curriculum.curriculum_loader import CurriculumLoader


class CurriculumLoaderTest(unittest.TestCase):
    def test_loads_existing_lab_curriculum(self) -> None:
        curriculum = CurriculumLoader(Path("curriculum")).load()

        lesson = curriculum.default_lesson()

        self.assertEqual(lesson.lesson_id, "P1LAB1")
        self.assertEqual(lesson.phase_id, "P1")
        self.assertEqual(curriculum.first_topic("P1LAB1"), "Learning State")
        self.assertEqual(curriculum.next_topic("P1LAB1", "Learning State"), "Teaching Workflow")
        self.assertIn("Learning State", curriculum.content_for("P1LAB1", "Learning State"))


if __name__ == "__main__":
    unittest.main()
