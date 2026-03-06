from typing import Any

import httpx

from app.config import settings


async def get_google_user_info(code: str) -> dict[str, Any]:
    """Exchange Google OAuth code for tokens and retrieve user info."""
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.FRONTEND_URL}/auth/google/callback",
                "grant_type": "authorization_code",
            },
        )
        token_response.raise_for_status()
        tokens = token_response.json()

        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        user_response.raise_for_status()
        return user_response.json()


async def get_github_user_info(code: str) -> dict[str, Any]:
    """Exchange GitHub OAuth code for tokens and retrieve user info."""
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_response.raise_for_status()
        tokens = token_response.json()

        access_token = tokens["access_token"]

        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        user_response.raise_for_status()
        user_data = user_response.json()

        # Get primary email if not public
        if not user_data.get("email"):
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            email_response.raise_for_status()
            emails = email_response.json()
            primary = next((e for e in emails if e.get("primary")), None)
            if primary:
                user_data["email"] = primary["email"]

        return user_data
