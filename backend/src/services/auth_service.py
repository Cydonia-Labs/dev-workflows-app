"""Authentication service for GitHub OAuth and JWT session management."""

from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.models.user import User
from src.services.token_encryption import decrypt_token, encrypt_token

# GitHub OAuth endpoints
GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"

# JWT configuration
JWT_ALGORITHM = "HS256"

# Session tokens expire after 7 days
SESSION_TTL_DAYS = 7


def build_authorize_url(state: str) -> str:
    """Build the GitHub OAuth authorization URL.

    Args:
        state: Random CSRF state parameter.

    Returns:
        The full authorization URL to redirect the user to.
    """
    settings = get_settings()
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": f"{settings.cors_origin_list[0]}/auth/callback",
        "scope": "repo",
        "state": state,
    }
    return f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> str:
    """Exchange an OAuth authorization code for a GitHub access token.

    Args:
        code: The authorization code from GitHub's OAuth callback.

    Returns:
        The GitHub access token.

    Raises:
        httpx.HTTPStatusError: If the token exchange fails.
        ValueError: If the response doesn't contain an access token.
    """
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_TOKEN_URL,
            json={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

    token = data.get("access_token")
    if not token:
        error = data.get("error_description", "Unknown error")
        raise ValueError(f"GitHub OAuth failed: {error}")

    return token


async def fetch_github_user(token: str) -> dict:
    """Fetch the authenticated user's profile from GitHub.

    Args:
        token: GitHub OAuth access token.

    Returns:
        A dict with the user's GitHub profile (id, login, name, avatar_url).

    Raises:
        httpx.HTTPStatusError: If the API call fails.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GITHUB_USER_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        response.raise_for_status()
        return response.json()


async def upsert_user(db: AsyncSession, github_user: dict, github_token: str) -> User:
    """Create or update a user record from GitHub profile data.

    If a user with the same github_id exists, updates their profile
    and token. Otherwise creates a new user. The GitHub token is
    encrypted before storage.

    Args:
        db: Database session.
        github_user: GitHub user profile dict (from fetch_github_user).
        github_token: The user's GitHub OAuth access token (plaintext).

    Returns:
        The created or updated User instance.
    """
    settings = get_settings()
    encrypted_token = encrypt_token(github_token, settings.secret_key)

    stmt = select(User).where(User.github_id == github_user["id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        user.github_login = github_user["login"]
        user.display_name = github_user.get("name") or github_user["login"]
        user.avatar_url = github_user.get("avatar_url")
        user.github_token = encrypted_token
    else:
        user = User(
            github_id=github_user["id"],
            github_login=github_user["login"],
            display_name=github_user.get("name") or github_user["login"],
            avatar_url=github_user.get("avatar_url"),
            github_token=encrypted_token,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user


def get_decrypted_github_token(user: User) -> str:
    """Decrypt a user's stored GitHub token for API calls.

    Args:
        user: The user whose token to decrypt.

    Returns:
        The plaintext GitHub OAuth token.

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails.
    """
    settings = get_settings()
    return decrypt_token(user.github_token, settings.secret_key)


def create_session_token(user_id: str) -> str:
    """Create a JWT session token for a user.

    Args:
        user_id: The user's UUID as a string.

    Returns:
        A signed JWT string.
    """
    settings = get_settings()
    payload = {
        "sub": user_id,
        "exp": datetime.now(UTC) + timedelta(days=SESSION_TTL_DAYS),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_session_token(token: str) -> dict:
    """Decode and validate a JWT session token.

    Args:
        token: The JWT string from the Authorization header.

    Returns:
        The decoded token payload.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is malformed or invalid.
    """
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
