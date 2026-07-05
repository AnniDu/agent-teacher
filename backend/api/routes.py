from __future__ import annotations

from fastapi import APIRouter, Request

from .schemas import ChatRequest, ChatResponse, ResetStateRequest, ResetStateResponse, StateSummary


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    app_state = request.app.state.learning_coach
    state = app_state.state_manager.load(payload.student_id)
    result = app_state.learning_loop.run(state, payload.message)
    app_state.state_manager.save(result.state)
    return ChatResponse(message=result.message, state=StateSummary.from_state(result.state))


@router.get("/state/{student_id}", response_model=StateSummary)
def get_state(student_id: str, request: Request) -> StateSummary:
    app_state = request.app.state.learning_coach
    state = app_state.state_manager.load(student_id)
    return StateSummary.from_state(state)


@router.post("/state/{student_id}/reset", response_model=ResetStateResponse)
def reset_state(
    student_id: str,
    payload: ResetStateRequest,
    request: Request,
) -> ResetStateResponse:
    app_state = request.app.state.learning_coach
    state = app_state.state_manager.reset(
        student_id,
        phase=payload.phase,
        lesson=payload.lesson,
        topic=payload.topic,
    )
    return ResetStateResponse(ok=True, state=StateSummary.from_state(state))
