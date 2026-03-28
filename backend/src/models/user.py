"""User model for GitHub OAuth authenticated users."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class User(Base):
    """A user authenticated via GitHub OAuth.

    Attributes:
        id: Unique identifier.
        github_id: GitHub's numeric user ID (unique across GitHub).
        github_login: GitHub username.
        display_name: User's display name from GitHub profile.
        avatar_url: URL to the user's GitHub avatar.
        github_token: Encrypted OAuth access token for GitHub API calls.
        created_at: When the user first authenticated.
        updated_at: When the user record was last updated.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    github_login: Mapped[str] = mapped_column(String(39), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    github_token: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
