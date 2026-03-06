import re
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException, BadRequestException
from app.models.user import User
from app.models.company import Company
from app.models.job import Job, Application
from app.schemas.job import (
    ApplicationResponse,
    ApplyRequest,
    CreateJobRequest,
    JobResponse,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
async def create_job(
    body: CreateJobRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("recruiter", "admin"):
        raise ForbiddenException("Only recruiters can create jobs")

    result = await db.execute(
        select(Company).where(Company.owner_id == current_user.id).limit(1)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise NotFoundException("You must create a company first")

    job = Job(
        company_id=company.id,
        title=body.title,
        description=body.description,
        required_skills=body.required_skills,
        min_overall_score=body.min_overall_score,
        is_active=body.is_active,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    is_active: bool = Query(True),
    skill: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Job).where(Job.is_active == is_active)
    result = await db.execute(query.order_by(Job.created_at.desc()))
    jobs = result.scalars().all()

    if skill:
        jobs = [j for j in jobs if skill.lower() in [s.lower() for s in (j.required_skills or [])]]

    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Job not found")
    return job


@router.post("/{job_id}/apply", response_model=ApplicationResponse)
async def apply_to_job(
    job_id: UUID,
    body: ApplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Job not found")

    # Check for duplicate application
    existing = await db.execute(
        select(Application).where(
            Application.job_id == job_id,
            Application.user_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise BadRequestException("You have already applied to this job")

    application = Application(
        job_id=job_id,
        user_id=current_user.id,
        status="pending",
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@router.get("/{job_id}/applicants", response_model=list[ApplicationResponse])
async def view_applicants(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("recruiter", "admin"):
        raise ForbiddenException("Only recruiters can view applicants")

    result = await db.execute(
        select(Application).where(Application.job_id == job_id)
    )
    return result.scalars().all()
