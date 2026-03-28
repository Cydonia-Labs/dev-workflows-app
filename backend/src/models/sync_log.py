"""Sync log model for tracking content sync operations from GitHub."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class SyncLog(Base):
    """An audit log entry for a content sync operation.

    Each row represents one webhook-triggered sync from GitHub.
    Used for debugging sync issues and tracking sync history.

    Attributes:
        id: Unique identifier.
        github_sha: The commit SHA that triggered the sync.
        status: Current status (started, completed, failed).
        files_updated: Number of document files updated during sync.
        error_message: Error details if the sync failed.
        started_at: When the sync operation began.
        completed_at: When the sync operation finished.
    """

    __tablename__ = "sync_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    files_updated: Mapped[int | None] = mapped_column(SmallInteger)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
