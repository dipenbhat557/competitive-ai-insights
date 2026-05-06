from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateJobRequest(BaseModel):
    title: str
    description: str
    required_skills: list[str] = []
    min_overall_score: Optional[float] = None
    is_active: bool = True


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    title: str
    description: str
    required_skills: list[Any] = []
    min_overall_score: Optional[float] = None
    is_active: bool
    created_at: datetime


class ApplyRequest(BaseModel):
    pass


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    user_id: UUID
    status: str
    ai_match_score: Optional[float] = None
    ai_match_reason: Optional[str] = None
    created_at: datetime


class ExternalJobResponse(BaseModel):
    """A live job posting fetched from an external public job board."""
    source: str
    source_id: str
    title: str
    company: str
    description: str
    required_skills: list[str] = []
    location: Optional[str] = None
    apply_url: Optional[str] = None
    posted_at: Optional[str] = None


class JobMatchResponse(BaseModel):
    """A scored job match for the current user."""
    job_id: Optional[UUID] = None  # null for external (non-DB) jobs
    source: str                     # "internal" | "remoteok" | "greenhouse:<board>"
    title: str
    company: str
    description: str
    required_skills: list[str] = []
    location: Optional[str] = None
    apply_url: Optional[str] = None
    match_score: float
    reasoning: str
    skill_gaps: list[str] = []
    highlights: list[str] = []
