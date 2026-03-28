"""FastAPI dependency functions for request-scoped resources.

Provides database sessions and authenticated user extraction
for use with FastAPI's Depends() system.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.services.auth_service import decode_session_token

# Bearer token extraction from Authorization header
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the authenticated user from the request.

    Decodes the JWT from the Authorization header, looks up the user
    in the database, and returns the User instance.

    Args:
        credentials: Bearer token from the Authorization header.
        db: Database session.

    Returns:
        The authenticated User instance.

    Raises:
        HTTPException(401): If the token is missing, expired, or invalid.
        HTTPException(401): If the user no longer exists in the database.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_session_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Optionally extract the authenticated user, returning None if not logged in.

    Useful for endpoints that work for both authenticated and anonymous users
    but may show extra features for logged-in users.

    Args:
        credentials: Bearer token from the Authorization header.
        db: Database session.

    Returns:
        The authenticated User instance, or None if not authenticated.
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
