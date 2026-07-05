from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from typing import Optional

from backend.config import load_settings
from backend.core.learning_loop import LearningLoop
from backend.curriculum.curriculum import Curriculum, Lesson, Topic
from backend.curriculum.curriculum_loader import CurriculumLoader
from backend.events.event_log import EventLog
from backend.services.assessment_service import AssessmentService
from backend.services.llm_client import TeachingResponse, parse_teaching_response
from backend.services.teaching_service import TeachingService, TeachingToolError
from backend.state.models import ASSESS_MODE
from backend.state.state_manager import StateManager
from backend.state.state_store import FileStateStore
from backend.tools.models import ToolCall, ToolContext
from backend.tools.registry import ToolError, default_tool_registry


class ToolRegistryTest(unittest.TestCase):
    def test_mode_policy_rejects_assess_mode_tools(self) -> None:
        context = _tool_context()
        registry = default_tool_registry()

        with self.assertRaisesRegex(ToolError, "not allowed"):
            registry.execute(ASSESS_MODE, ToolCall("get_current_topic", {}), context)

    def test_tools_do_not_mutate_state(self) -> None:
        context = _tool_context()
        registry = default_tool_registry()
        before = copy.deepcopy(context.state.to_dict())

        registry.execute("teach", ToolCall("get_current_topic", {}), context)
        registry.execute("teach", ToolCall("get_student_learning_summary", {}), context)
        registry.execute("teach", ToolCall("search_curriculum", {"query": "state"}), context)

        self.assertEqual(context.state.to_dict(), before)

    def test_search_curriculum_bounds_results_and_prioritizes_current_phase(self) -> None:
        curriculum = Curriculum(
            [
                Lesson(
                    lesson_id="P1L1",
                    phase_id="P1",
                    title="Phase One State",
                    path="p1.md",
                    content="state alpha state beta",
                    topics=[Topic("P1 Topic A", "state alpha"), Topic("P1 Topic B", "state beta")],
                ),
                Lesson(
                    lesson_id="P0L1",
                    phase_id="P0",
                    title="Phase Zero State",
                    path="p0.md",
                    content="state gamma state delta",
                    topics=[Topic("P0 Topic A", "state gamma"), Topic("P0 Topic B", "state delta")],
                ),
            ],
            default_lesson_id="P1L1",
        )
        context = _tool_context(curriculum=curriculum, lesson_id="P1L1", topic_name="P1 Topic A")
        result = default_tool_registry().execute(
            "teach",
            ToolCall("search_curriculum", {"query": "state"}),
            context,
        )

        matches = result.content["matches"]
        self.assertLessEqual(len(matches), 3)
        self.assertEqual(matches[0]["phase"], "P1")
        self.assertIn("excerpt", matches[0])
        self.assertIn("lesson_id", matches[0])

    def test_student_learning_summary_omits_workflow_control_fields(self) -> None:
        context = _tool_context()
        context.state.next_step = "wait_for_answer"
        context.state.current_mode = "assess"

        result = default_tool_registry().execute(
            "teach",
            ToolCall("get_student_learning_summary", {}),
            context,
        )

        self.assertNotIn("next_step", result.content)
        self.assertNotIn("current_mode", result.content)


class TeachingToolingTest(unittest.TestCase):
    def test_successful_allowed_tool_call_and_result_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            components = _components(
                Path(tmpdir),
                _FakeLlm(
                    [
                        _tool_call("get_current_topic", {}),
                        _teaching_response("Tool-informed explanation.", "Tool question?"),
                    ]
                ),
            )
            state = components.state_manager.initial_state("student-1")

            result = components.learning_loop.run(state, "start")

            self.assertEqual(result.state.current_mode, "assess")
            self.assertIn("Tool-informed explanation.", result.message)
            self.assertEqual(len(components.llm.prompts), 2)
            self.assertIn("Tool result:", components.llm.prompts[1])
            self.assertIn("Scalar, Vector, Matrix, Tensor", components.llm.prompts[1])

    def test_unknown_tool_rejection_logs_failed_tool_call(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            components = _components(root, _FakeLlm([_tool_call("unknown_tool", {})]))
            state = components.state_manager.initial_state("student-1")

            with self.assertRaises(TeachingToolError):
                components.learning_loop.run(state, "start")

            events = _events(root, "student-1")
            tool_events = [event for event in events if event["type"] == "tool_call"]
            self.assertEqual(len(tool_events), 1)
            self.assertFalse(tool_events[0]["succeeded"])
            self.assertEqual(tool_events[0]["tool_name"], "unknown_tool")

    def test_second_tool_call_is_rejected_and_logged(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            components = _components(
                root,
                _FakeLlm(
                    [
                        _tool_call("get_current_topic", {}),
                        _tool_call("get_student_learning_summary", {}),
                    ]
                ),
            )
            state = components.state_manager.initial_state("student-1")

            with self.assertRaisesRegex(TeachingToolError, "second tool request"):
                components.learning_loop.run(state, "start")

            tool_event = [event for event in _events(root, "student-1") if event["type"] == "tool_call"][0]
            self.assertFalse(tool_event["succeeded"])
            self.assertEqual(tool_event["tool_name"], "get_current_topic")

    def test_final_teaching_response_without_tool_still_works(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            components = _components(Path(tmpdir), _FakeLlm([_teaching_response()]))
            state = components.state_manager.initial_state("student-1")

            result = components.learning_loop.run(state, "start")

            self.assertEqual(result.state.current_mode, "assess")
            self.assertIn("Learning state tracks progress.", result.message)
            self.assertEqual(len(components.llm.prompts), 1)

    def test_tool_call_event_is_written_by_learning_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            components = _components(
                root,
                _FakeLlm(
                    [
                        _tool_call("get_student_learning_summary", {}),
                        _teaching_response(),
                    ]
                ),
            )
            state = components.state_manager.initial_state("student-1")

            components.learning_loop.run(state, "start")

            event_types = [event["type"] for event in _events(root, "student-1")]
            self.assertEqual(
                event_types,
                ["student_message", "tool_call", "state_transition", "assistant_message"],
            )

    def test_teaching_service_consumes_provider_neutral_response_model(self) -> None:
        parsed = parse_teaching_response(_teaching_response())

        self.assertIsInstance(parsed, TeachingResponse)


class _Components:
    def __init__(self, state_manager: StateManager, learning_loop: LearningLoop, llm: "_FakeLlm") -> None:
        self.state_manager = state_manager
        self.learning_loop = learning_loop
        self.llm = llm


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
    return _Components(state_manager, learning_loop, llm)


def _tool_context(
    curriculum: Optional[Curriculum] = None,
    lesson_id: str = "P0L1",
    topic_name: str = "Scalar, Vector, Matrix, Tensor",
) -> ToolContext:
    curriculum = curriculum or CurriculumLoader(Path("curriculum")).load()
    settings = load_settings(Path(tempfile.mkdtemp()))
    manager = StateManager(FileStateStore(settings.data_dir), curriculum)
    state = manager.initial_state("student-1", lesson=lesson_id, topic=topic_name)
    lesson = curriculum.lesson(lesson_id)
    topic = curriculum.topic(lesson_id, topic_name)
    return ToolContext(state=state, curriculum=curriculum, lesson=lesson, topic=topic)


def _teaching_response(
    explanation: str = "Learning state tracks progress.",
    question: str = "What is learning state?",
) -> str:
    return json.dumps(
        {
            "type": "teaching_response",
            "explanation": explanation,
            "question": question,
        }
    )


def _tool_call(name: str, arguments: dict) -> str:
    return json.dumps({"type": "tool_call", "tool": {"name": name, "arguments": arguments}})


def _events(root: Path, student_id: str) -> list:
    lines = (root / "data" / "events" / f"{student_id}.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


if __name__ == "__main__":
    unittest.main()
