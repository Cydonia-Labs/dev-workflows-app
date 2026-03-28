"""Pydantic schemas for notification and push subscription endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class PushKeys(BaseModel):
    """Web Push subscription encryption keys.

    Attributes:
        p256dh: Client P-256 public key for message encryption.
        auth: Client authentication secret.
    """

    p256dh: str = Field(min_length=1, max_length=500)
    auth: str = Field(min_length=1, max_length=500)


class PushSubscriptionRequest(BaseModel):
    """Request body for registering a Web Push subscription.

    Attributes:
        endpoint: The push service endpoint URL.
        keys: Encryption keys from the browser's PushSubscription.
    """

    endpoint: str = Field(min_length=1, max_length=2048)
    keys: PushKeys


class NotificationResponse(BaseModel):
    """A single notification for the user.

    Attributes:
        id: Notification unique identifier.
        type: Event type (new_comment, pr_submitted, etc.).
        title: Short notification title.
        body: Notification body text.
        link: Deep link into the app.
        is_read: Whether the user has seen this notification.
        created_at: When the notification was created.
    """

    id: str
    type: str
    title: str
    body: str
    link: str | None
    is_read: bool
    created_at: datetime


class MarkReadRequest(BaseModel):
    """Request body for marking notifications as read.

    Attributes:
        notification_ids: List of notification IDs to mark as read. Maximum 100 per request.
    """

    notification_ids: list[str] = Field(max_length=100)


class VapidKeyResponse(BaseModel):
    """Response containing the VAPID public key for push setup.

    Attributes:
        public_key: The VAPID public key string.
    """

    public_key: str
