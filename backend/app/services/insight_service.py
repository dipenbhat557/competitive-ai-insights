from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.insight import InsightReport
from app.models.profile import CodingProfile, PlatformSnapshot
from app.services.ai.insight_generator import InsightGenerator


async def generate_insights(
    user_id: UUID, db: AsyncSession, force: bool = False
) -> InsightReport:
    # If not forcing, check for a recent report
    if not force:
        result = await db.execute(
            select(InsightReport)
            .where(InsightReport.user_id == user_id)
            .order_by(InsightReport.created_at.desc())
            .limit(1)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    # Gather all snapshots for the user
    result = await db.execute(
        select(CodingProfile).where(CodingProfile.user_id == user_id)
    )
    profiles = result.scalars().all()

    if not profiles:
        raise NotFoundException("No linked profiles found. Link a coding profile first.")

    all_snapshots = []
    for profile in profiles:
        result = await db.execute(
            select(PlatformSnapshot)
            .where(PlatformSnapshot.profile_id == profile.id)
            .order_by(PlatformSnapshot.scraped_at.desc())
            .limit(1)
        )
        snapshot = result.scalar_one_or_none()
        if snapshot:
            all_snapshots.append({
                "platform": profile.platform,
                "username": profile.platform_username,
                "problems_solved": snapshot.problems_solved,
                "contest_rating": snapshot.contest_rating,
                "topic_stats": snapshot.topic_stats,
                "submission_calendar": snapshot.submission_calendar,
            })

    if not all_snapshots:
        raise NotFoundException("No scraped data found. Scrape your profiles first.")

    generator = InsightGenerator()
    insight_data = await generator.generate(all_snapshots)

    report = InsightReport(
        user_id=user_id,
        strengths=insight_data.get("strengths", []),
        weaknesses=insight_data.get("weaknesses", []),
        career_recs=insight_data.get("career_recs", []),
        roadmap=insight_data.get("roadmap", []),
        overall_score=insight_data.get("overall_score", 0.0),
        summary_text=insight_data.get("summary_text", ""),
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report
