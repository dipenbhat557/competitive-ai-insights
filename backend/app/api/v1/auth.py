from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    OAuthCodeRequest,
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


@router.post("/oauth/google", response_model=TokenResponse)
async def oauth_google(body: OAuthCodeRequest, db: AsyncSession = Depends(get_db)):
    return await get_or_create_oauth_user(body.code, "google", db)


@router.post("/oauth/github", response_model=TokenResponse)
async def oauth_github(body: OAuthCodeRequest, db: AsyncSession = Depends(get_db)):
    return await get_or_create_oauth_user(body.code, "github", db)
