import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models import Base


class CodingProfile(Base):
    __tablename__ = "coding_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)
    platform_username = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="coding_profiles")
    snapshots = relationship("PlatformSnapshot", back_populates="profile", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "platform", name="uq_user_platform"),
    )


class PlatformSnapshot(Base):
    __tablename__ = "platform_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("coding_profiles.id", ondelete="CASCADE"), nullable=False)
    problems_solved = Column(Integer, default=0, nullable=False)
    contest_rating = Column(Float, nullable=True)
    topic_stats = Column(JSONB, default=dict)
    submission_calendar = Column(JSONB, default=dict)
    raw_data = Column(JSONB, default=dict)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("CodingProfile", back_populates="snapshots")
