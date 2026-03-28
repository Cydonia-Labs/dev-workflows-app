"""Push subscription model for Web Push API notification delivery."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class PushSubscription(Base):
    """A Web Push API subscription for a user's browser/device.

    Each subscription represents one browser on one device. A user
    can have multiple subscriptions (phone, laptop, etc.). Stale
    subscriptions are cleaned up when the push service returns 410 Gone.

    Attributes:
        id: Unique identifier.
        user_id: The user who owns this subscription.
        endpoint: The push service endpoint URL.
        p256dh_key: The client's P-256 public key for message encryption.
        auth_key: The client's authentication secret.
        created_at: When the subscription was registered.
        user: The owning user relationship.
    """

    __tablename__ = "push_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    endpoint: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    p256dh_key: Mapped[str] = mapped_column(Text, nullable=False)
    auth_key: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
