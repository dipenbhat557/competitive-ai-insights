from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LinkProfileRequest(BaseModel):
    platform: str
    platform_username: str


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    platform: str
    platform_username: str
    created_at: datetime


class SnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    problems_solved: int
    contest_rating: Optional[float] = None
    topic_stats: dict[str, Any] = {}
    submission_calendar: dict[str, Any] = {}
    scraped_at: datetime


class ScrapeResponse(BaseModel):
    message: str
    profiles: list[ProfileResponse]
