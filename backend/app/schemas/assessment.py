from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QuestionCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    test_cases: list[Any] = []
    order_index: int = 0


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    difficulty: str
    test_cases: list[Any] = []
    order_index: int


class CreateAssessmentRequest(BaseModel):
    title: str
    description: Optional[str] = None
    time_limit_mins: int = 60


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    title: str
    description: Optional[str] = None
    time_limit_mins: int
    created_at: datetime
    questions: list[QuestionResponse] = []


class SubmissionCreate(BaseModel):
    question_id: UUID
    code: str
    language: str


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question_id: UUID
    user_id: UUID
    code: str
    language: str
    status: str
    score: Optional[float] = None
    ai_feedback: Optional[str] = None
    submitted_at: datetime
