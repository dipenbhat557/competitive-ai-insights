from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.oauth import get_github_user_info, get_google_user_info
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserOAuth
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def _build_tokens(user: User) -> TokenResponse:
    data = {"sub": str(user.id)}
    return TokenResponse(
        access_token=create_access_token(data),
        refresh_token=create_refresh_token(data),
    )


async def register_user(body: RegisterRequest, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise BadRequestException("Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _build_tokens(user)


async def authenticate_user(body: LoginRequest, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise UnauthorizedException("Invalid email or password")

    if not verify_password(body.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")

    return _build_tokens(user)


async def refresh_tokens(refresh_token: str, db: AsyncSession) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise UnauthorizedException("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedException("User not found")

    return _build_tokens(user)


async def get_or_create_oauth_user(
    code: str, provider: str, db: AsyncSession
) -> TokenResponse:
    if provider == "google":
        user_info = await get_google_user_info(code)
        provider_uid = user_info.get("id", "")
        email = user_info.get("email", "")
        full_name = user_info.get("name", "")
        avatar_url = user_info.get("picture", "")
    elif provider == "github":
        user_info = await get_github_user_info(code)
        provider_uid = str(user_info.get("id", ""))
        email = user_info.get("email", "")
        full_name = user_info.get("name") or user_info.get("login", "")
        avatar_url = user_info.get("avatar_url", "")
    else:
        raise BadRequestException(f"Unsupported provider: {provider}")

    if not email:
        raise BadRequestException("Could not retrieve email from OAuth provider")

    # Check if OAuth link exists
    result = await db.execute(
        select(UserOAuth).where(
            UserOAuth.provider == provider,
            UserOAuth.provider_uid == provider_uid,
        )
    )
    oauth_record = result.scalar_one_or_none()

    if oauth_record:
        result = await db.execute(select(User).where(User.id == oauth_record.user_id))
        user = result.scalar_one()
        if not user.avatar_url and avatar_url:
            user.avatar_url = avatar_url
            await db.commit()
            await db.refresh(user)
        return _build_tokens(user)

    # Check if user with this email already exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(email=email, full_name=full_name, avatar_url=avatar_url or None)
        db.add(user)
        await db.flush()
    elif not user.avatar_url and avatar_url:
        user.avatar_url = avatar_url

    oauth_link = UserOAuth(
        user_id=user.id,
        provider=provider,
        provider_uid=provider_uid,
    )
    db.add(oauth_link)
    await db.commit()
    await db.refresh(user)

    return _build_tokens(user)
