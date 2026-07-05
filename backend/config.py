from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    data_dir: Path
    curriculum_dir: Path
    gemini_api_key: Optional[str]
    gemini_model: str
    assessment_pass_threshold: float = 0.8


def load_settings(repo_root: Optional[Path] = None) -> Settings:
    root = (repo_root or Path.cwd()).resolve()
    _load_env_file(root / ".env")
    return Settings(
        repo_root=root,
        data_dir=Path(os.environ.get("LEARNING_COACH_DATA_DIR", root / "data")).resolve(),
        curriculum_dir=Path(
            os.environ.get("LEARNING_COACH_CURRICULUM_DIR", root / "curriculum")
        ).resolve(),
        gemini_api_key=os.environ.get("GEMINI_API_KEY"),
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
    )


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
