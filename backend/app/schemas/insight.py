from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    strengths: list[Any] = []
    weaknesses: list[Any] = []
    career_recs: list[Any] = []
    roadmap: list[Any] = []
    overall_score: float
    summary_text: Optional[str] = None
    created_at: datetime


class GenerateInsightRequest(BaseModel):
    force_regenerate: Optional[bool] = False
