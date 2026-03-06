from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.chat import ChatMessage, ChatSession
from app.models.insight import InsightReport
from app.services.ai.chat_engine import ChatEngine


async def create_session(
    user_id: UUID, title: str, db: AsyncSession
) -> ChatSession:
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_sessions(user_id: UUID, db: AsyncSession) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
    )
    return result.scalars().all()


async def get_session_with_messages(
    user_id: UUID, session_id: UUID, db: AsyncSession
) -> dict:
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Session not found")
    if session.user_id != user_id:
        raise ForbiddenException("Not your session")

    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in session.messages
        ],
    }


async def send_message(
    session_id: UUID, content: str, user_id: UUID, db: AsyncSession
) -> tuple[ChatMessage, ChatMessage]:
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Session not found")
    if session.user_id != user_id:
        raise ForbiddenException("Not your session")

    # Store user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=content,
    )
    db.add(user_msg)

    # Build chat history
    history = [{"role": m.role, "content": m.content} for m in session.messages]
    history.append({"role": "user", "content": content})

    # Fetch user profile context
    result = await db.execute(
        select(InsightReport)
        .where(InsightReport.user_id == user_id)
        .order_by(InsightReport.created_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    profile_context = ""
    if report:
        profile_context = report.summary_text or ""

    # Get AI response
    engine = ChatEngine()
    ai_response = await engine.get_response(history, profile_context)

    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_response,
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(user_msg)
    await db.refresh(assistant_msg)
    return user_msg, assistant_msg


async def delete_session(user_id: UUID, session_id: UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Session not found")
    if session.user_id != user_id:
        raise ForbiddenException("Not your session")

    await db.delete(session)
    await db.commit()
