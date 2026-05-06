import asyncio
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
    ExternalJobResponse,
    JobMatchResponse,
    JobResponse,
)
from app.services.ai.skill_matcher import SkillMatcher
from app.services.scraper.jobs import ExternalJob, ExternalJobsScraper
from app.services.profile_service import get_user_profiles_with_snapshots
from app.services.normalizer import Normalizer

router = APIRouter(prefix="/jobs", tags=["jobs"])


# ---------------------------------------------------------------------------
# Internal job CRUD
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# External jobs + AI-powered matching
# IMPORTANT: literal-path routes must be declared BEFORE /{job_id} so they
# aren't shadowed by UUID-path matching.
# ---------------------------------------------------------------------------


@router.get("/external/live", response_model=list[ExternalJobResponse])
async def list_external_jobs(
    limit: int = Query(25, ge=1, le=100),
):
    """Fetch live job postings from public job boards (no DB persistence)."""
    scraper = ExternalJobsScraper()
    jobs = await scraper.fetch_all(limit_per_source=limit)
    return [ExternalJobResponse(**j.to_dict()) for j in jobs]


def _build_candidate_profile(profiles_payload: dict) -> dict:
    """Build a normalized candidate-profile dict for the AI skill matcher.

    Uses the cross-platform Normalizer so the matcher reasons over canonical
    topics + percentile ratings instead of mixing raw scales (LC 1700 != CF 1700).
    """
    snapshots = profiles_payload.get("snapshots", [])
    profiles = profiles_payload.get("profiles", [])

    platforms_linked: list[str] = []
    snapshot_dicts: list[dict] = []

    for prof, snap in zip(profiles, snapshots):
        platform = getattr(prof, "platform", None) or (
            prof.get("platform") if isinstance(prof, dict) else None
        )
        if not platform:
            continue
        platforms_linked.append(platform)
        snapshot_dicts.append({
            "platform": platform,
            "username": getattr(prof, "platform_username", None) or (
                prof.get("platform_username") if isinstance(prof, dict) else None
            ),
            "problems_solved": snap.get("problems_solved", 0),
            "contest_rating": snap.get("contest_rating"),
            "topic_stats": snap.get("topic_stats") or {},
            "raw_data": snap.get("raw_data") or {},
        })

    if not snapshot_dicts:
        return {"platforms_linked": platforms_linked}

    agg = Normalizer.aggregate(snapshot_dicts)
    top_canonical = sorted(
        agg.canonical_topic_stats.items(), key=lambda x: -x[1]
    )[:15]

    return {
        "platforms_linked": platforms_linked,
        "total_problems_raw": agg.total_problems_raw,
        "weighted_problem_volume": agg.total_weighted_volume,
        "rating_percentile_overall": agg.rating_percentile_overall,
        "rating_percentile_per_platform": agg.rating_percentile_per_platform,
        "canonical_top_topics": [
            {"topic": agg.label_for.get(t, t), "count": c}
            for t, c in top_canonical
        ],
        "difficulty_breakdown": agg.difficulty_breakdown,
        "topic_coverage": agg.coverage,
    }


@router.get("/matches", response_model=list[JobMatchResponse])
async def match_jobs(
    include_external: bool = Query(True),
    top_n: int = Query(8, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rank internal + external jobs against the current user's coding profile."""
    profiles_payload = await get_user_profiles_with_snapshots(current_user.id, db)
    candidate_profile = _build_candidate_profile(profiles_payload)

    if not candidate_profile["platforms_linked"]:
        raise BadRequestException(
            "Link at least one coding profile and run a scrape before matching jobs"
        )

    # Internal jobs
    internal_result = await db.execute(
        select(Job).where(Job.is_active == True).order_by(Job.created_at.desc()).limit(20)  # noqa: E712
    )
    internal_jobs = internal_result.scalars().all()

    # External jobs (optional)
    external_jobs: list[ExternalJob] = []
    if include_external:
        scraper = ExternalJobsScraper()
        try:
            external_jobs = await scraper.fetch_all(limit_per_source=10)
        except Exception:
            external_jobs = []

    matcher = SkillMatcher()

    async def _score_internal(job: Job) -> JobMatchResponse:
        skills = [s for s in (job.required_skills or []) if isinstance(s, str)]
        result = await matcher.match(
            candidate_profile=candidate_profile,
            job_title=job.title,
            job_description=job.description,
            required_skills=skills,
            min_score=job.min_overall_score,
        )
        return JobMatchResponse(
            job_id=job.id,
            source="internal",
            title=job.title,
            company="",
            description=job.description,
            required_skills=skills,
            location=None,
            apply_url=None,
            **result,
        )

    async def _score_external(job: ExternalJob) -> JobMatchResponse:
        result = await matcher.match(
            candidate_profile=candidate_profile,
            job_title=job.title,
            job_description=job.description,
            required_skills=job.required_skills,
            min_score=None,
        )
        return JobMatchResponse(
            job_id=None,
            source=job.source,
            title=job.title,
            company=job.company,
            description=job.description[:600],
            required_skills=job.required_skills,
            location=job.location,
            apply_url=job.apply_url,
            **result,
        )

    # Cap how many we send to Gemini to keep latency/cost reasonable.
    coros = [_score_internal(j) for j in internal_jobs[:8]] + [
        _score_external(j) for j in external_jobs[:12]
    ]
    scored = await asyncio.gather(*coros, return_exceptions=True)
    matches = [m for m in scored if isinstance(m, JobMatchResponse)]
    matches.sort(key=lambda m: m.match_score, reverse=True)
    return matches[:top_n]


# ---------------------------------------------------------------------------
# Job detail / applications (UUID-pathed routes — declared LAST)
# ---------------------------------------------------------------------------


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
