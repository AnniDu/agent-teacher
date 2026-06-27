from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .curriculum_loader import CurriculumLoader
from .llm_client import LLMError, default_llm_client
from .models import LearningContext
from .prompt_builder import build_state_update_prompt, build_teaching_prompt
from .state_loader import StateLoader
from .state_updater import StateUpdater


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Teach the current curriculum lesson.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing curriculum/ and state/. Defaults to current directory.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    try:
        _load_env_file(repo_root / ".env")
        context = _load_context(repo_root)
        llm = default_llm_client()

        teaching_prompt = build_teaching_prompt(context)
        teaching_response = llm.generate(teaching_prompt)
        print(teaching_response)

        state_prompt = build_state_update_prompt(context, teaching_response)
        state_response = llm.generate(state_prompt)
        StateUpdater(repo_root).apply(state_response, context)
    except (RuntimeError, OSError, LLMError) as exc:
        print(f"learn: error: {exc}", file=sys.stderr)
        return 1
    return 0


def _load_context(repo_root: Path) -> LearningContext:
    state_loader = StateLoader(repo_root)
    navigation = state_loader.load_navigation()
    location = state_loader.current_location(navigation)
    curriculum = CurriculumLoader(repo_root).load_for_location(location)
    state = state_loader.load_for_location(location, curriculum.previous_lesson_id)
    return LearningContext(curriculum=curriculum, state=state)


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
