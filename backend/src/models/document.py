"""Document model for handbook markdown files."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Document(Base):
    """A markdown document from the handbook repository.

    Each row represents one .md file from the docs/ directory.
    Content is synced from GitHub via webhook and stored for
    fast reads and per-section features.

    Attributes:
        id: Unique identifier.
        slug: URL-friendly identifier derived from filename (e.g., "git-branching").
        filename: Original filename in the repo (e.g., "git-branching.md").
        title: Document title extracted from the H1 heading.
        raw_markdown: Full markdown content of the file.
        github_sha: Git commit SHA at the time of last sync.
        sort_order: Display order based on README table of contents.
        synced_at: When this document was last synced from GitHub.
        created_at: When the document was first added to the database.
        updated_at: When the document record was last modified.
        sections: Parsed sections within this document.
    """

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    github_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")
