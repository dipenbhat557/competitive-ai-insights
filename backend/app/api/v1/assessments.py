from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.deps import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.user import User
from app.models.company import Company
from app.models.assessment import Assessment, AssessmentQuestion, Submission
from app.schemas.assessment import (
    AssessmentResponse,
    CreateAssessmentRequest,
    QuestionCreate,
    SubmissionCreate,
    SubmissionResponse,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentResponse)
async def create_assessment(
    body: CreateAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("recruiter", "admin"):
        raise ForbiddenException("Only recruiters can create assessments")

    # Find a company owned by this user
    result = await db.execute(
        select(Company).where(Company.owner_id == current_user.id).limit(1)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise NotFoundException("You must create a company first")

    assessment = Assessment(
        company_id=company.id,
        title=body.title,
        description=body.description,
        time_limit_mins=body.time_limit_mins,
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    # Reload with questions relationship
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.questions))
        .where(Assessment.id == assessment.id)
    )
    return result.scalar_one()


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.questions))
        .where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise NotFoundException("Assessment not found")
    return assessment


@router.post("/{assessment_id}/questions")
async def add_question(
    assessment_id: UUID,
    body: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("recruiter", "admin"):
        raise ForbiddenException("Only recruiters can add questions")

    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise NotFoundException("Assessment not found")

    question = AssessmentQuestion(
        assessment_id=assessment_id,
        title=body.title,
        description=body.description,
        difficulty=body.difficulty,
        test_cases=body.test_cases,
        order_index=body.order_index,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


@router.post("/{assessment_id}/submit", response_model=list[SubmissionResponse])
async def submit_answers(
    assessment_id: UUID,
    body: list[SubmissionCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise NotFoundException("Assessment not found")

    submissions = []
    for item in body:
        submission = Submission(
            question_id=item.question_id,
            user_id=current_user.id,
            code=item.code,
            language=item.language,
            status="submitted",
        )
        db.add(submission)
        submissions.append(submission)

    await db.commit()
    for s in submissions:
        await db.refresh(s)
    return submissions


@router.get("/{assessment_id}/submissions", response_model=list[SubmissionResponse])
async def view_submissions(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("recruiter", "admin"):
        raise ForbiddenException("Only recruiters can view all submissions")

    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.questions))
        .where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise NotFoundException("Assessment not found")

    question_ids = [q.id for q in assessment.questions]
    if not question_ids:
        return []

    result = await db.execute(
        select(Submission).where(Submission.question_id.in_(question_ids))
    )
    return result.scalars().all()
