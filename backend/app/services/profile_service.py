from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from app.models.profile import CodingProfile, PlatformSnapshot
from app.models.user import User
from app.schemas.profile import LinkProfileRequest, ProfileResponse, ScrapeResponse
from app.services.scraper.aggregator import ProfileAggregator
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


async def link_profile(
    user_id: UUID, body: LinkProfileRequest, db: AsyncSession
) -> CodingProfile:
    platform = body.platform.lower()
    if platform not in SCRAPERS:
        raise BadRequestException(f"Unsupported platform: {body.platform}")

    result = await db.execute(
        select(CodingProfile).where(
            CodingProfile.user_id == user_id,
            CodingProfile.platform == platform,
        )
    )
    if result.scalar_one_or_none():
        raise BadRequestException(f"You already have a {platform} profile linked")

    profile = CodingProfile(
        user_id=user_id,
        platform=platform,
        platform_username=body.platform_username,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def unlink_profile(user_id: UUID, profile_id: UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(CodingProfile).where(CodingProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundException("Profile not found")
    if profile.user_id != user_id:
        raise ForbiddenException("Not your profile")

    await db.delete(profile)
    await db.commit()


async def _do_scrape(profile: CodingProfile, db: AsyncSession) -> None:
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
        pass  # Scraping failures are non-fatal


async def scrape_all_profiles(
    user_id: UUID, db: AsyncSession, background_tasks: BackgroundTasks
) -> ScrapeResponse:
    result = await db.execute(
        select(CodingProfile).where(CodingProfile.user_id == user_id)
    )
    profiles = result.scalars().all()

    if not profiles:
        raise NotFoundException("No linked profiles found")

    for profile in profiles:
        background_tasks.add_task(_do_scrape, profile, db)

    return ScrapeResponse(
        message=f"Scraping started for {len(profiles)} profile(s)",
        profiles=[ProfileResponse.model_validate(p) for p in profiles],
    )


async def scrape_platform(
    user_id: UUID, platform: str, db: AsyncSession, background_tasks: BackgroundTasks
) -> ScrapeResponse:
    platform = platform.lower()
    result = await db.execute(
        select(CodingProfile).where(
            CodingProfile.user_id == user_id,
            CodingProfile.platform == platform,
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundException(f"No {platform} profile linked")

    background_tasks.add_task(_do_scrape, profile, db)

    return ScrapeResponse(
        message=f"Scraping started for {platform}",
        profiles=[ProfileResponse.model_validate(profile)],
    )


async def get_user_profiles(user_id: UUID, db: AsyncSession) -> list[CodingProfile]:
    result = await db.execute(
        select(CodingProfile).where(CodingProfile.user_id == user_id)
    )
    return result.scalars().all()


async def get_user_profiles_with_snapshots(user_id: UUID, db: AsyncSession) -> dict:
    profiles = await get_user_profiles(user_id, db)
    snapshots = []
    for profile in profiles:
        result = await db.execute(
            select(PlatformSnapshot)
            .where(PlatformSnapshot.profile_id == profile.id)
            .order_by(PlatformSnapshot.scraped_at.desc())
            .limit(1)
        )
        snapshot = result.scalar_one_or_none()
        if snapshot:
            snapshots.append(snapshot)
    return {
        "profiles": [ProfileResponse.model_validate(p) for p in profiles],
        "snapshots": [
            {
                "id": str(s.id),
                "problems_solved": s.problems_solved,
                "contest_rating": s.contest_rating,
                "topic_stats": s.topic_stats,
                "submission_calendar": s.submission_calendar,
                "scraped_at": s.scraped_at.isoformat() if s.scraped_at else None,
            }
            for s in snapshots
        ],
    }


async def get_public_profile(username: str, db: AsyncSession) -> list[CodingProfile]:
    result = await db.execute(
        select(User).where(User.full_name == username)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")

    return await get_user_profiles(user.id, db)


async def get_snapshot_history(
    user_id: UUID, profile_id: UUID, db: AsyncSession
) -> list[PlatformSnapshot]:
    result = await db.execute(
        select(CodingProfile).where(CodingProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundException("Profile not found")
    if profile.user_id != user_id:
        raise ForbiddenException("Not your profile")

    result = await db.execute(
        select(PlatformSnapshot)
        .where(PlatformSnapshot.profile_id == profile_id)
        .order_by(PlatformSnapshot.scraped_at.desc())
    )
    return result.scalars().all()
