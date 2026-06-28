from __future__ import annotations

import json

import yaml

from .models import LearningContext


def build_teaching_prompt(context: LearningContext) -> str:
    lesson_note = context.state.lesson_note or "(no lesson notes yet)"
    previous_lesson_note = context.state.previous_lesson_note or "(no previous lesson notes available)"
    return f"""You are a patient, precise Learning Agent teaching one lesson from a local curriculum.

Teach only the current lesson. Do not jump ahead. Be clear, interactive, and practical.
Use the curriculum as the source of truth. Ask the learner 1-3 short check questions near the end.

## Course Index
{context.curriculum.course_index}

## Current Phase Index
{context.curriculum.phase_index}

## Current Lesson
{context.curriculum.lesson}

## Current Phase Progress
{yaml.safe_dump(context.state.progress, sort_keys=False)}

## Review Queue
{yaml.safe_dump(context.state.review_queue, sort_keys=False)}

## Previous Lesson Notes
{previous_lesson_note}

## Current Lesson Notes
{lesson_note}
"""


def build_state_update_prompt(context: LearningContext, teaching_response: str) -> str:
    example = {
        "state_update": {
            "navigation": context.state.navigation,
            "progress": {
                "phase": context.curriculum.phase_id,
                "lesson_id": context.curriculum.lesson_id,
                "status": "in_progress",
                "score": None,
                "weak_topics": [],
                "completed_topics": [],
            },
            "review_queue": {"add": [], "remove": []},
            "lesson_note": {
                "lesson_id": context.curriculum.lesson_id,
                "summary": "",
                "weak_points": [],
                "aha_moments": [],
                "next_action": "",
            },
        }
    }
    return f"""Return a minimal JSON state update for the lesson session.

Rules:
- Return only valid JSON. No Markdown fences.
- The LLM must not write files; it only proposes structured data.
- Do not mark the lesson completed unless the teaching response clearly completed it.
- Prefer status "in_progress" for this MVP teaching run.
- Keep navigation unchanged unless the learner clearly completed the lesson.
- Keep arrays empty when there is no evidence.

## Current State
navigation:
{yaml.safe_dump(context.state.navigation, sort_keys=False)}
progress:
{yaml.safe_dump(context.state.progress, sort_keys=False)}
review_queue:
{yaml.safe_dump(context.state.review_queue, sort_keys=False)}

## Teaching Response
{teaching_response}

## Required JSON Shape
{json.dumps(example, indent=2)}
"""


def build_assessment_prompt(
    context: LearningContext, teaching_output: str, learner_response: str
) -> str:
    example = {
        "assessment": {
            "lesson_id": context.curriculum.lesson_id,
            "summary": "",
            "evidence": [],
            "gaps": [],
            "feedback": "",
        },
        "state_update": {
            "navigation": context.state.navigation,
            "progress": {
                "phase": context.curriculum.phase_id,
                "lesson_id": context.curriculum.lesson_id,
                "status": "in_progress",
                "score": None,
                "weak_topics": [],
                "completed_topics": [],
            },
            "review_queue": {"add": [], "remove": []},
            "lesson_note": {
                "lesson_id": context.curriculum.lesson_id,
                "summary": "",
                "weak_points": [],
                "aha_moments": [],
                "next_action": "",
            },
        },
    }
    lesson_goal = _lesson_goal(context.curriculum.lesson)
    return f"""Assess the learner response for the current lesson.

Rules:
- Return only valid JSON. No Markdown fences.
- The LLM must not write files; it only proposes structured data.
- Evaluate the learner response, not the teaching output.
- Never infer mastery from teaching output alone.
- Only mark topics completed when learner evidence supports it.
- If learner evidence is weak or missing, keep status "in_progress".
- Keep arrays empty when there is no evidence.

## Current Lesson Goal
{lesson_goal}

## Course Index
{context.curriculum.course_index}

## Current Phase Index
{context.curriculum.phase_index}

## Current Lesson
{context.curriculum.lesson}

## Current State
navigation:
{yaml.safe_dump(context.state.navigation, sort_keys=False)}
progress:
{yaml.safe_dump(context.state.progress, sort_keys=False)}
review_queue:
{yaml.safe_dump(context.state.review_queue, sort_keys=False)}

## Teaching Output
{teaching_output}

## Learner Response
{learner_response}

## Required JSON Shape
{json.dumps(example, indent=2)}
"""


def _lesson_goal(lesson: str) -> str:
    for line in lesson.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered.startswith("**goal:**"):
            return stripped.split("**", 2)[-1].strip()
        if lowered.startswith("goal:"):
            return stripped.split(":", 1)[1].strip()
    return "(use the current lesson content as the lesson goal)"
