from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatMessageResponse,
    ChatSessionResponse,
    CreateSessionRequest,
    SendMessageRequest,
)
from app.services.chat_service import (
    create_session,
    delete_session,
    get_session_with_messages,
    get_sessions,
    send_message,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse)
async def create(
    body: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_session(current_user.id, body.title or "New Chat", db)


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_sessions(current_user.id, db)


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_session_with_messages(current_user.id, session_id, db)


@router.post("/sessions/{session_id}/messages")
async def send(
    session_id: UUID,
    body: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_msg, assistant_msg = await send_message(session_id, body.content, current_user.id, db)
    return {
        "user_message": ChatMessageResponse.model_validate(user_msg),
        "assistant_message": ChatMessageResponse.model_validate(assistant_msg),
    }


@router.delete("/sessions/{session_id}")
async def delete(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_session(current_user.id, session_id, db)
    return {"detail": "Session deleted"}
