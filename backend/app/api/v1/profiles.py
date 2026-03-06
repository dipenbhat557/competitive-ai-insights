from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.profile import (
    LinkProfileRequest,
    ProfileResponse,
    ScrapeResponse,
    SnapshotResponse,
)
from app.services.profile_service import (
    get_public_profile,
    get_snapshot_history,
    get_user_profiles,
    link_profile,
    scrape_all_profiles,
    scrape_platform,
    unlink_profile,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/link", response_model=ProfileResponse)
async def link(
    body: LinkProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await link_profile(current_user.id, body, db)


@router.delete("/{profile_id}")
async def unlink(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await unlink_profile(current_user.id, profile_id, db)
    return {"detail": "Profile unlinked"}


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_all(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await scrape_all_profiles(current_user.id, db, background_tasks)


@router.post("/scrape/{platform}", response_model=ScrapeResponse)
async def scrape_single(
    platform: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await scrape_platform(current_user.id, platform, db, background_tasks)


@router.get("")
async def list_profiles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.profile_service import get_user_profiles_with_snapshots
    return await get_user_profiles_with_snapshots(current_user.id, db)


@router.get("/{username}/public", response_model=list[ProfileResponse])
async def public_profile(username: str, db: AsyncSession = Depends(get_db)):
    return await get_public_profile(username, db)


@router.get("/{profile_id}/history", response_model=list[SnapshotResponse])
async def snapshot_history(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_snapshot_history(current_user.id, profile_id, db)
