"""Notification service for in-app and push notification delivery.

Creates notification records and sends Web Push messages to
subscribed browsers/devices.
"""

import json
import logging

from pywebpush import WebPushException, webpush
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.models.notification import Notification
from src.models.push_subscription import PushSubscription

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    user_id,
    notification_type: str,
    title: str,
    body: str,
    link: str | None = None,
) -> Notification:
    """Create a notification and attempt to send it via push.

    Args:
        db: Database session.
        user_id: UUID of the target user.
        notification_type: Event type (new_comment, pr_submitted, etc.).
        title: Short notification title.
        body: Notification body text.
        link: Deep link into the app for this notification.

    Returns:
        The created Notification instance.
    """
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        body=body,
        link=link,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    # Send push notification to all user's subscriptions
    push_sent = await _send_push_to_user(db, user_id, title, body, link)
    if push_sent:
        notification.push_sent = True
        await db.commit()

    return notification


async def get_notifications_for_user(
    db: AsyncSession,
    user_id,
    limit: int = 50,
    offset: int = 0,
) -> list[Notification]:
    """Fetch notifications for a user, newest first.

    Args:
        db: Database session.
        user_id: UUID of the user.
        limit: Maximum number of notifications to return.
        offset: Number of notifications to skip.

    Returns:
        A list of Notification instances.
    """
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def mark_notifications_read(
    db: AsyncSession,
    user_id,
    notification_ids: list,
) -> int:
    """Mark specified notifications as read.

    Args:
        db: Database session.
        user_id: UUID of the user (for authorization).
        notification_ids: List of notification UUIDs to mark read.

    Returns:
        The number of notifications updated.
    """
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.id.in_(notification_ids))
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def save_push_subscription(
    db: AsyncSession,
    user_id,
    endpoint: str,
    p256dh_key: str,
    auth_key: str,
) -> PushSubscription:
    """Save or update a Web Push subscription.

    If a subscription with the same endpoint already exists, updates
    the keys. Otherwise creates a new subscription.

    Args:
        db: Database session.
        user_id: UUID of the subscribing user.
        endpoint: Push service endpoint URL.
        p256dh_key: Client P-256 public key.
        auth_key: Client authentication secret.

    Returns:
        The created or updated PushSubscription.
    """
    stmt = select(PushSubscription).where(PushSubscription.endpoint == endpoint)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    if sub:
        sub.user_id = user_id
        sub.p256dh_key = p256dh_key
        sub.auth_key = auth_key
    else:
        sub = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh_key,
            auth_key=auth_key,
        )
        db.add(sub)

    await db.commit()
    await db.refresh(sub)
    return sub


async def remove_push_subscription(db: AsyncSession, endpoint: str) -> None:
    """Remove a Web Push subscription by endpoint.

    Args:
        db: Database session.
        endpoint: The push service endpoint URL to remove.
    """
    stmt = select(PushSubscription).where(PushSubscription.endpoint == endpoint)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()
    if sub:
        await db.delete(sub)
        await db.commit()


async def _send_push_to_user(
    db: AsyncSession,
    user_id,
    title: str,
    body: str,
    link: str | None,
) -> bool:
    """Send a Web Push notification to all of a user's subscribed devices.

    Args:
        db: Database session.
        user_id: UUID of the target user.
        title: Notification title.
        body: Notification body.
        link: Deep link URL.

    Returns:
        True if at least one push was sent successfully.
    """
    settings = get_settings()
    if not settings.vapid_private_key:
        return False

    stmt = select(PushSubscription).where(PushSubscription.user_id == user_id)
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()

    if not subscriptions:
        return False

    payload = json.dumps({"title": title, "body": body, "link": link})
    any_sent = False

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
                },
                data=payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={
                    "sub": f"mailto:{settings.vapid_claim_email}",
                },
            )
            any_sent = True
        except WebPushException as e:
            # 410 Gone means the subscription is no longer valid
            if hasattr(e, "response") and e.response is not None and e.response.status_code == 410:
                logger.info("Removing stale push subscription: %s", sub.endpoint)
                await db.delete(sub)
                await db.commit()
            else:
                logger.warning("Push notification failed for %s: %s", sub.endpoint, e)

    return any_sent
