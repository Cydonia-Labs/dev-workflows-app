"""Authentication routes for GitHub OAuth login flow."""

import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.auth import TokenResponse, UserResponse
from src.services.auth_service import (
    build_authorize_url,
    create_session_token,
    exchange_code_for_token,
    fetch_github_user,
    upsert_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory state store for CSRF protection.
# In production with multiple instances, use Redis or signed state.
_oauth_states: set[str] = set()


@router.get("/github")
async def github_login() -> RedirectResponse:
    """Redirect the user to GitHub's OAuth authorization page.

    Returns:
        A redirect response to GitHub's authorization URL.
    """
    state = secrets.token_urlsafe(32)
    _oauth_states.add(state)
    url = build_authorize_url(state)
    return RedirectResponse(url=url)


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Handle the GitHub OAuth callback after user authorization.

    Exchanges the authorization code for an access token, fetches the
    user's GitHub profile, creates or updates the user record, and
    returns a JWT session token.

    Args:
        code: Authorization code from GitHub.
        state: CSRF state parameter to validate.
        db: Database session.

    Returns:
        A TokenResponse with the session JWT and user profile.

    Raises:
        HTTPException(400): If the state parameter is invalid.
        HTTPException(502): If GitHub OAuth token exchange fails.
    """
    if state not in _oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    _oauth_states.discard(state)

    try:
        github_token = await exchange_code_for_token(code)
    except Exception as exc:
        logger.exception("GitHub OAuth token exchange failed")
        raise HTTPException(status_code=502, detail="Authentication failed") from exc

    github_user = await fetch_github_user(github_token)
    user = await upsert_user(db, github_user, github_token)

    session_token = create_session_token(str(user.id))

    return TokenResponse(
        access_token=session_token,
        user=UserResponse(
            id=str(user.id),
            github_login=user.github_login,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_admin=user.is_admin,
        ),
    )


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user's profile.

    Args:
        user: The authenticated user (from JWT).

    Returns:
        The user's public profile.
    """
    return UserResponse(
        id=str(user.id),
        github_login=user.github_login,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        is_admin=user.is_admin,
    )


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)) -> dict[str, str]:
    """Log out the current user.

    In a stateless JWT setup, the client discards the token.
    This endpoint exists for future token blocklisting.

    Args:
        user: The authenticated user.

    Returns:
        A confirmation message.
    """
    return {"status": "logged out"}
