from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers
from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="CodePulse AI", version="1.0.0", lifespan=lifespan)

# FRONTEND_URL accepts either a single URL (legacy) or a comma-separated list.
# Vercel preview deploys are matched by regex so PRs work without env churn.
allow_origins = [
    o.strip() for o in (settings.FRONTEND_URL or "").split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"^https://([a-z0-9-]+\.)?vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
register_exception_handlers(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
