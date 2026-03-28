"""Section model for parsed heading-level sections within a document."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Section(Base):
    """A parsed section within a handbook document.

    Documents are split at H2 and H3 headings during content sync.
    Each section has an anchor for deep linking and can have threaded
    comments attached to it.

    Attributes:
        id: Unique identifier.
        document_id: Parent document this section belongs to.
        anchor: URL-safe anchor derived from the heading text.
        title: The heading text.
        heading_level: 2 for H2, 3 for H3.
        content: Markdown content between this heading and the next.
        sort_order: Position within the parent document.
        parent_section_id: For H3 sections, the parent H2 section.
        created_at: When the section was created during sync.
        document: The parent document relationship.
        parent_section: The parent H2 section (for H3 sections).
        children: Child H3 sections (for H2 sections).
        comments: Threaded comments on this section.
    """

    __tablename__ = "sections"
    __table_args__ = (UniqueConstraint("document_id", "anchor"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    anchor: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    heading_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    parent_section_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    document = relationship("Document", back_populates="sections")
    parent_section = relationship("Section", remote_side=[id], backref="children")
    comments = relationship("Comment", back_populates="section", cascade="all, delete-orphan")
