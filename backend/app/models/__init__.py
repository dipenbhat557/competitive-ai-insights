from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.user import User, UserOAuth  # noqa: E402
from app.models.profile import CodingProfile, PlatformSnapshot  # noqa: E402
from app.models.insight import InsightReport  # noqa: E402
from app.models.chat import ChatSession, ChatMessage  # noqa: E402
from app.models.company import Company  # noqa: E402
from app.models.assessment import Assessment, AssessmentQuestion, Submission  # noqa: E402
from app.models.job import Job, Application  # noqa: E402

__all__ = [
    "Base",
    "User",
    "UserOAuth",
    "CodingProfile",
    "PlatformSnapshot",
    "InsightReport",
    "ChatSession",
    "ChatMessage",
    "Company",
    "Assessment",
    "AssessmentQuestion",
    "Submission",
    "Job",
    "Application",
]
