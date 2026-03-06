from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.insight import InsightReport
from app.schemas.insight import GenerateInsightRequest, InsightResponse
from app.services.insight_service import generate_insights

router = APIRouter(prefix="/insights", tags=["insights"])


@router.post("/generate", response_model=InsightResponse)
async def generate(
    body: GenerateInsightRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await generate_insights(current_user.id, db, force=body.force_regenerate or False)


@router.get("/latest", response_model=InsightResponse | None)
async def latest(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InsightReport)
        .where(InsightReport.user_id == current_user.id)
        .order_by(InsightReport.created_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    return report


@router.get("/history", response_model=list[InsightResponse])
async def history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InsightReport)
        .where(InsightReport.user_id == current_user.id)
        .order_by(InsightReport.created_at.desc())
    )
    return result.scalars().all()
