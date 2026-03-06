"""Background task functions for scraping coding profiles."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.profile import CodingProfile, PlatformSnapshot
from app.services.scraper.leetcode import LeetCodeScraper
from app.services.scraper.codeforces import CodeforcesScraper
from app.services.scraper.codechef import CodeChefScraper
from app.services.scraper.hackerrank import HackerRankScraper

SCRAPERS = {
    "leetcode": LeetCodeScraper(),
    "codeforces": CodeforcesScraper(),
    "codechef": CodeChefScraper(),
    "hackerrank": HackerRankScraper(),
}


async def scrape_user_profiles(user_id: UUID) -> None:
    """
    Background task to scrape all linked profiles for a user.
    Creates its own database session since it runs outside of a request context.
    """
    async with async_session() as db:
        result = await db.execute(
            select(CodingProfile).where(CodingProfile.user_id == user_id)
        )
        profiles = result.scalars().all()

        for profile in profiles:
            await _scrape_single_profile(profile, db)


async def scrape_single_platform(user_id: UUID, platform: str) -> None:
    """
    Background task to scrape a single platform profile.
    """
    async with async_session() as db:
        result = await db.execute(
            select(CodingProfile).where(
                CodingProfile.user_id == user_id,
                CodingProfile.platform == platform.lower(),
            )
        )
        profile = result.scalar_one_or_none()
        if profile:
            await _scrape_single_profile(profile, db)


async def _scrape_single_profile(profile: CodingProfile, db: AsyncSession) -> None:
    """Scrape a single profile and store the snapshot."""
    scraper = SCRAPERS.get(profile.platform)
    if not scraper:
        return

    try:
        data = await scraper.scrape(profile.platform_username)
        snapshot = PlatformSnapshot(
            profile_id=profile.id,
            problems_solved=data.problems_solved,
            contest_rating=data.contest_rating,
            topic_stats=data.topic_stats,
            submission_calendar=data.submission_calendar,
            raw_data=data.raw_data,
        )
        db.add(snapshot)
        await db.commit()
    except Exception:
        # Log the error in production; non-fatal for background tasks
        await db.rollback()
