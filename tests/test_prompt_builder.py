from __future__ import annotations

import unittest
from pathlib import Path

from agent_teacher.models import CurriculumContext, LearningContext, StateContext
from agent_teacher.prompt_builder import build_assessment_prompt


class AssessmentPromptBuilderTest(unittest.TestCase):
    def test_assessment_prompt_includes_evidence_context_and_rules(self) -> None:
        context = LearningContext(
            curriculum=CurriculumContext(
                course_index="# Course",
                phase_index="# Phase",
                lesson='**Goal:** Understand vector meaning.\n\nLesson body',
                phase_id="P0",
                lesson_id="P0L1",
                previous_lesson_id=None,
                lesson_path=Path("curriculum/phase0/lesson01-intro.md"),
            ),
            state=StateContext(
                navigation={"current": {"phase": "P0", "lesson": "P0L1", "topic": None}},
                progress={"phase": "P0", "lessons": []},
                review_queue={"queue": []},
                lesson_note=None,
                previous_lesson_note=None,
                lesson_note_path=Path("state/lesson_notes/P0L1.md"),
            ),
        )

        prompt = build_assessment_prompt(
            context,
            teaching_output="Teaching output",
            learner_response="Learner response",
        )

        self.assertIn("Return only valid JSON", prompt)
        self.assertIn("Never infer mastery from teaching output alone", prompt)
        self.assertIn("Understand vector meaning.", prompt)
        self.assertIn("Teaching output", prompt)
        self.assertIn("Learner response", prompt)
        self.assertIn('"assessment"', prompt)
        self.assertIn('"state_update"', prompt)


if __name__ == "__main__":
    unittest.main()
