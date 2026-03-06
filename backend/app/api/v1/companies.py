import re

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.user import User
from app.models.company import Company
from app.models.assessment import Assessment
from app.models.job import Job, Application
from app.schemas.company import CompanyResponse, CreateCompanyRequest

router = APIRouter(prefix="/companies", tags=["companies"])


def _slugify(name: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[\s_]+", "-", slug).strip("-")


@router.post("", response_model=CompanyResponse)
async def create_company(
    body: CreateCompanyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("recruiter", "admin"):
        raise ForbiddenException("Only recruiters can create companies")

    slug = _slugify(body.name)

    existing = await db.execute(select(Company).where(Company.slug == slug))
    if existing.scalar_one_or_none():
        raise BadRequestException("A company with this name already exists")

    company = Company(
        name=body.name,
        slug=slug,
        owner_id=current_user.id,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


@router.get("/{slug}", response_model=CompanyResponse)
async def get_company(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.slug == slug))
    company = result.scalar_one_or_none()
    if not company:
        raise NotFoundException("Company not found")
    return company


@router.patch("/{slug}", response_model=CompanyResponse)
async def update_company(
    slug: str,
    body: CreateCompanyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).where(Company.slug == slug))
    company = result.scalar_one_or_none()
    if not company:
        raise NotFoundException("Company not found")
    if company.owner_id != current_user.id:
        raise ForbiddenException("You do not own this company")

    company.name = body.name
    company.slug = _slugify(body.name)
    await db.commit()
    await db.refresh(company)
    return company


@router.get("/{slug}/dashboard")
async def company_dashboard(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).where(Company.slug == slug))
    company = result.scalar_one_or_none()
    if not company:
        raise NotFoundException("Company not found")
    if company.owner_id != current_user.id:
        raise ForbiddenException("You do not own this company")

    assessment_count = await db.execute(
        select(func.count(Assessment.id)).where(Assessment.company_id == company.id)
    )
    job_count = await db.execute(
        select(func.count(Job.id)).where(Job.company_id == company.id)
    )
    application_count = await db.execute(
        select(func.count(Application.id))
        .join(Job, Application.job_id == Job.id)
        .where(Job.company_id == company.id)
    )

    return {
        "company": CompanyResponse.model_validate(company),
        "total_assessments": assessment_count.scalar() or 0,
        "total_jobs": job_count.scalar() or 0,
        "total_applications": application_count.scalar() or 0,
    }
