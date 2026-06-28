from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from .curriculum_loader import CurriculumLoader
from .llm_client import LLMError, default_llm_client
from .memory_store import JsonMemoryStore, MemoryRecord
from .models import LearningContext
from .prompt_builder import build_assessment_prompt, build_state_update_prompt, build_teaching_prompt
from .state_loader import StateLoader
from .state_updater import StateUpdater


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Teach or assess the current curriculum lesson.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing curriculum/ and state/. Defaults to current directory.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("teach", "assess"),
        help="Workflow to run. Defaults to teaching the current lesson.",
    )
    parser.add_argument(
        "--response",
        help="Learner response file for the assess workflow.",
    )
    args = parser.parse_args(argv)
    if args.command == "assess" and not args.response:
        parser.error("learn assess requires --response <path>")
    if args.command != "assess" and args.response:
        parser.error("--response can only be used with learn assess")

    repo_root = Path(args.repo_root).resolve()
    try:
        _load_env_file(repo_root / ".env")
        context = _load_context(repo_root)
        llm = default_llm_client()
        if args.command == "assess":
            _run_assessment(repo_root, context, llm, Path(args.response))
        else:
            _run_teaching(repo_root, context, llm)
    except (RuntimeError, OSError, LLMError) as exc:
        print(f"learn: error: {exc}", file=sys.stderr)
        return 1
    return 0


def _run_teaching(repo_root: Path, context: LearningContext, llm: object) -> None:
    teaching_prompt = build_teaching_prompt(context)
    teaching_response = llm.generate(teaching_prompt)
    print(teaching_response)
    _save_teaching_output(repo_root, context, teaching_response)

    state_prompt = build_state_update_prompt(context, teaching_response)
    state_response = llm.generate(state_prompt)
    StateUpdater(repo_root).apply(state_response, context)


def _run_assessment(
    repo_root: Path, context: LearningContext, llm: object, response_path: Path
) -> None:
    memory_store = JsonMemoryStore(repo_root)
    teaching_record = memory_store.latest(context.curriculum.lesson_id, "teaching")
    if teaching_record is None:
        raise RuntimeError(
            f"No teaching output found in memory for {context.curriculum.lesson_id}"
        )

    resolved_response_path = _resolve_repo_path(repo_root, response_path)
    learner_response = resolved_response_path.read_text()
    _save_learner_response(repo_root, context, learner_response, resolved_response_path)

    assessment_prompt = build_assessment_prompt(
        context,
        teaching_record.content,
        learner_response,
    )
    assessment_response = llm.generate(assessment_prompt)
    _save_assessment_output(repo_root, context, assessment_response)
    StateUpdater(repo_root).apply(assessment_response, context)


def _load_context(repo_root: Path) -> LearningContext:
    state_loader = StateLoader(repo_root)
    navigation = state_loader.load_navigation()
    location = state_loader.current_location(navigation)
    curriculum = CurriculumLoader(repo_root).load_for_location(location)
    state = state_loader.load_for_location(location, curriculum.previous_lesson_id)
    return LearningContext(curriculum=curriculum, state=state)


def _save_teaching_output(repo_root: Path, context: LearningContext, teaching_response: str) -> None:
    record = MemoryRecord(
        record_id=f"{context.curriculum.lesson_id}:teaching",
        lesson_id=context.curriculum.lesson_id,
        record_type="teaching",
        content=teaching_response,
        metadata=_memory_metadata(context),
        created_at=_utc_now(),
    )
    JsonMemoryStore(repo_root).save(record)


def _save_learner_response(
    repo_root: Path, context: LearningContext, learner_response: str, response_path: Path
) -> None:
    metadata = _memory_metadata(context)
    metadata["response_path"] = str(response_path)
    record = MemoryRecord(
        record_id=f"{context.curriculum.lesson_id}:learner_response",
        lesson_id=context.curriculum.lesson_id,
        record_type="learner_response",
        content=learner_response,
        metadata=metadata,
        created_at=_utc_now(),
    )
    JsonMemoryStore(repo_root).save(record)


def _save_assessment_output(repo_root: Path, context: LearningContext, assessment_output: str) -> None:
    record = MemoryRecord(
        record_id=f"{context.curriculum.lesson_id}:assessment",
        lesson_id=context.curriculum.lesson_id,
        record_type="assessment",
        content=assessment_output,
        metadata=_memory_metadata(context),
        created_at=_utc_now(),
    )
    JsonMemoryStore(repo_root).save(record)


def _memory_metadata(context: LearningContext) -> dict[str, str]:
    curriculum = context.curriculum
    return {
        "phase": curriculum.phase_id,
        "lesson_id": curriculum.lesson_id,
        "lesson_path": str(curriculum.lesson_path),
    }


def _resolve_repo_path(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


if __name__ == "__main__":
    raise SystemExit(main())
