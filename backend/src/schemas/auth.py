"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Public user profile returned by the API.

    Attributes:
        id: Unique user identifier.
        github_login: GitHub username.
        display_name: Display name from GitHub profile.
        avatar_url: URL to GitHub avatar image.
    """

    id: str
    github_login: str
    display_name: str
    avatar_url: str | None


class TokenResponse(BaseModel):
    """Response returned after successful OAuth authentication.

    Attributes:
        access_token: JWT session token for subsequent API calls.
        token_type: Always "bearer".
        user: The authenticated user's profile.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
