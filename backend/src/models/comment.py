"""Comment model for threaded discussions on document sections."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Comment(Base):
    """A threaded comment on a document section.

    Comments can be top-level (parent_id is None) or replies to
    another comment. Threads can be marked as resolved.

    Attributes:
        id: Unique identifier.
        section_id: The section this comment is attached to.
        author_id: The user who wrote the comment.
        parent_id: The parent comment if this is a reply, None if top-level.
        body: The comment text (markdown).
        is_resolved: Whether this thread has been marked as resolved.
        created_at: When the comment was posted.
        updated_at: When the comment was last edited.
        section: The section this comment belongs to.
        author: The user who wrote this comment.
        parent: The parent comment (for replies).
        replies: Child replies to this comment.
    """

    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE")
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    section = relationship("Section", back_populates="comments")
    author = relationship("User")
    parent = relationship("Comment", remote_side=[id], backref="replies")
