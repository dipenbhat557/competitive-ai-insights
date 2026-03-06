import uuid
from datetime import datetime

from sqlalchemy import Column, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models import Base


class InsightReport(Base):
    __tablename__ = "insight_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strengths = Column(JSONB, default=list)
    weaknesses = Column(JSONB, default=list)
    career_recs = Column(JSONB, default=list)
    roadmap = Column(JSONB, default=list)
    overall_score = Column(Float, default=0.0)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="insight_reports")
