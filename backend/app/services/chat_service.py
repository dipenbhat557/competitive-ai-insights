import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.chat import ChatMessage, ChatSession
from app.models.insight import InsightReport
from app.models.profile import CodingProfile, PlatformSnapshot
from app.models.user import User
from app.services.ai.chat_engine import ChatEngine


def _build_profile_context(
    user: User,
    profiles: list[CodingProfile],
    snapshots: list[PlatformSnapshot],
    report: InsightReport | None,
) -> str:
    """Build a rich text context from the user's data for the AI mentor."""
    parts = [f"User: {user.full_name} ({user.email})"]

    if not profiles:
        parts.append("No coding platforms linked yet.")
        return "\n".join(parts)

    # Per-platform stats
    total_solved = 0
    for profile in profiles:
        snap = next((s for s in snapshots if s.profile_id == profile.id), None)
        if not snap:
            parts.append(f"\n--- {profile.platform.upper()} ({profile.platform_username}) ---")
            parts.append("  No scraped data yet.")
            continue

        parts.append(f"\n--- {profile.platform.upper()} ({profile.platform_username}) ---")
        parts.append(f"  Problems Solved: {snap.problems_solved}")
        total_solved += snap.problems_solved

        if snap.contest_rating:
            parts.append(f"  Contest Rating: {snap.contest_rating:.0f}")

        # Difficulty breakdown from raw_data
        raw = snap.raw_data or {}
        matched_user = raw.get("profile", {}).get("matchedUser", {})
        ac_stats = matched_user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
        diff_parts = []
        for ac in ac_stats:
            if ac.get("difficulty") != "All":
                diff_parts.append(f"{ac['difficulty']}: {ac['count']}")
        if diff_parts:
            parts.append(f"  Difficulty: {', '.join(diff_parts)}")

        # Top topics
        if snap.topic_stats:
            sorted_topics = sorted(snap.topic_stats.items(), key=lambda x: x[1], reverse=True)
            top = sorted_topics[:10]
            parts.append(f"  Top Topics: {', '.join(f'{t}({c})' for t, c in top)}")
            if len(sorted_topics) > 10:
                bottom = sorted_topics[-5:]
                parts.append(f"  Weakest Topics: {', '.join(f'{t}({c})' for t, c in bottom)}")

    parts.append(f"\nTotal Problems Across All Platforms: {total_solved}")

    # AI insight report if available
    if report:
        parts.append("\n--- LATEST AI INSIGHT REPORT ---")
        parts.append(f"Overall Score: {report.overall_score}/100")
        if report.summary_text:
            parts.append(f"Summary: {report.summary_text}")
        if report.strengths:
            strengths_str = ", ".join(f"{s['topic']}({s['score']}%)" for s in report.strengths)
            parts.append(f"Strengths: {strengths_str}")
        if report.weaknesses:
            weaknesses_str = ", ".join(f"{w['topic']}({w['score']}%)" for w in report.weaknesses)
            parts.append(f"Weaknesses: {weaknesses_str}")
        if report.career_recs:
            parts.append(f"Career Recommendations: {'; '.join(report.career_recs)}")
        if report.roadmap:
            for phase in report.roadmap:
                parts.append(f"Roadmap [{phase.get('range', '')}]: {phase.get('focus', '')} — {', '.join(phase.get('actions', []))}")

    return "\n".join(parts)


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

    # Fetch user, profiles, snapshots, and insight report for context
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one()

    profiles_result = await db.execute(
        select(CodingProfile).where(CodingProfile.user_id == user_id)
    )
    profiles = list(profiles_result.scalars().all())

    snapshots = []
    for profile in profiles:
        snap_result = await db.execute(
            select(PlatformSnapshot)
            .where(PlatformSnapshot.profile_id == profile.id)
            .order_by(PlatformSnapshot.scraped_at.desc())
            .limit(1)
        )
        snap = snap_result.scalar_one_or_none()
        if snap:
            snapshots.append(snap)

    report_result = await db.execute(
        select(InsightReport)
        .where(InsightReport.user_id == user_id)
        .order_by(InsightReport.created_at.desc())
        .limit(1)
    )
    report = report_result.scalar_one_or_none()

    profile_context = _build_profile_context(user, profiles, snapshots, report)

    # Get AI response
    engine = ChatEngine()
    ai_response = await engine.get_response(history, profile_context)

    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_response,
    )
    db.add(assistant_msg)

    # Auto-generate session title from the first message
    if len(session.messages) == 0:
        try:
            title_engine = ChatEngine()
            title = await title_engine.client.generate_content(
                f"Generate a short title (max 6 words, no quotes) for a chat that starts with this message:\n\n{content}"
            )
            session.title = title.strip().strip('"\'')[:60]
        except Exception:
            session.title = content[:50] + ("..." if len(content) > 50 else "")

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
