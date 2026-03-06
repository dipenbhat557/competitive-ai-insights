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
