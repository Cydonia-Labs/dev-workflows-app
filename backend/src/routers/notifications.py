"""Notification and push subscription routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.notifications import (
    MarkReadRequest,
    NotificationResponse,
    PushSubscriptionRequest,
    VapidKeyResponse,
)
from src.services.notification_service import (
    get_notifications_for_user,
    mark_notifications_read,
    remove_push_subscription,
    save_push_subscription,
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[NotificationResponse]:
    """Return the authenticated user's notifications, newest first.

    Args:
        user: The authenticated user.
        db: Database session.
        limit: Maximum number to return. Defaults to 50.
        offset: Number to skip for pagination. Defaults to 0.

    Returns:
        A list of notifications.
    """
    notifications = await get_notifications_for_user(db, user.id, limit, offset)
    return [
        NotificationResponse(
            id=str(n.id),
            type=n.type,
            title=n.title,
            body=n.body,
            link=n.link,
            is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in notifications
    ]


@router.post("/read")
async def mark_read(
    body: MarkReadRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Mark specified notifications as read.

    Args:
        body: List of notification IDs to mark read.
        user: The authenticated user.
        db: Database session.

    Returns:
        The number of notifications updated.
    """
    count = await mark_notifications_read(db, user.id, body.notification_ids)
    return {"updated": count}


@router.post("/subscribe", status_code=201)
async def subscribe_push(
    body: PushSubscriptionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Register a Web Push subscription for the current user/device.

    Args:
        body: The PushSubscription object from the browser.
        user: The authenticated user.
        db: Database session.

    Returns:
        A confirmation message.
    """
    await save_push_subscription(
        db,
        user_id=user.id,
        endpoint=body.endpoint,
        p256dh_key=body.keys.p256dh,
        auth_key=body.keys.auth,
    )
    return {"status": "subscribed"}


@router.delete("/subscribe")
async def unsubscribe_push(
    body: PushSubscriptionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Unregister a Web Push subscription.

    Args:
        body: The subscription to remove (matched by endpoint).
        user: The authenticated user.
        db: Database session.

    Returns:
        A confirmation message.
    """
    await remove_push_subscription(db, body.endpoint)
    return {"status": "unsubscribed"}


@router.get("/vapid-key")
async def get_vapid_key() -> VapidKeyResponse:
    """Return the VAPID public key for push notification setup.

    Returns:
        The VAPID public key string.
    """
    settings = get_settings()
    return VapidKeyResponse(public_key=settings.vapid_public_key)
