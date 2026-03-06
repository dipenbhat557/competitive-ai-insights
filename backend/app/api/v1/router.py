from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.insights import router as insights_router
from app.api.v1.chat import router as chat_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.companies import router as companies_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(users_router)
api_router.include_router(profiles_router)
api_router.include_router(insights_router)
api_router.include_router(chat_router)
api_router.include_router(assessments_router)
api_router.include_router(jobs_router)
api_router.include_router(companies_router)
