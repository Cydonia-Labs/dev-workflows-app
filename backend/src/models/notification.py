"""Notification model for in-app and push notification tracking."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Notification(Base):
    """A notification for a user about an event that needs attention.

    Notifications are created by backend services when events occur
    (new comment, PR submitted, etc.) and are delivered both in-app
    and via Web Push.

    Attributes:
        id: Unique identifier.
        user_id: The user this notification is for.
        type: Event type (new_comment, pr_submitted, review_requested, pr_merged).
        title: Short notification title.
        body: Notification body text.
        link: Deep link into the app for this notification.
        is_read: Whether the user has seen this notification.
        push_sent: Whether a push notification was successfully delivered.
        created_at: When the notification was created.
        user: The target user relationship.
    """

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str | None] = mapped_column(String(2048))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    push_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    user = relationship("User")
