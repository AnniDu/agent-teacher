from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router
from backend.config import Settings, load_settings
from backend.core.learning_loop import LearningLoop
from backend.curriculum.curriculum_loader import CurriculumLoader
from backend.events.event_log import EventLog
from backend.services.assessment_service import AssessmentService
from backend.services.llm_client import GeminiClient, LLMClient
from backend.services.teaching_service import TeachingService
from backend.state.state_manager import StateManager
from backend.state.state_store import FileStateStore


@dataclass
class LearningCoachAppState:
    settings: Settings
    state_manager: StateManager
    learning_loop: LearningLoop


def create_app(repo_root: Optional[Path] = None, llm_client: Optional[LLMClient] = None) -> FastAPI:
    settings = load_settings(repo_root)
    curriculum = CurriculumLoader(settings.curriculum_dir).load()
    state_store = FileStateStore(settings.data_dir)
    state_manager = StateManager(state_store, curriculum)
    llm = llm_client or GeminiClient(settings)
    event_log = EventLog(settings.data_dir)
    learning_loop = LearningLoop(
        curriculum=curriculum,
        teaching_service=TeachingService(llm),
        assessment_service=AssessmentService(llm),
        event_log=event_log,
        settings=settings,
    )
    app = FastAPI(title="Learning Coach Agent")
    app.state.learning_coach = LearningCoachAppState(
        settings=settings,
        state_manager=state_manager,
        learning_loop=learning_loop,
    )
    app.include_router(router)
    frontend_dir = settings.repo_root / "frontend"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    return app


app = create_app()
