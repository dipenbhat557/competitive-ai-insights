from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import (
    authenticate_user,
    get_or_create_oauth_user,
    refresh_tokens,
    register_user,
)

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_user(body, db)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(body, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_tokens(body.refresh_token, db)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


# --- Google OAuth ---

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_REDIRECT_URI = "http://localhost:8000/api/v1/auth/oauth/google/callback"


@router.get("/oauth/google")
async def oauth_google_redirect():
    params = urlencode({
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    })
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{params}")


@router.get("/oauth/google/callback")
async def oauth_google_callback(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    tokens = await get_or_create_oauth_user(code, "google", db)
    params = urlencode({
        "token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
    })
    return RedirectResponse(f"{settings.FRONTEND_URL}/oauth/callback?{params}")


# --- GitHub OAuth ---

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_REDIRECT_URI = "http://localhost:8000/api/v1/auth/oauth/github/callback"


@router.get("/oauth/github")
async def oauth_github_redirect():
    params = urlencode({
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "user:email",
    })
    return RedirectResponse(f"{GITHUB_AUTH_URL}?{params}")


@router.get("/oauth/github/callback")
async def oauth_github_callback(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    tokens = await get_or_create_oauth_user(code, "github", db)
    params = urlencode({
        "token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
    })
    return RedirectResponse(f"{settings.FRONTEND_URL}/oauth/callback?{params}")
