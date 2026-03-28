"""GitHub webhook handler for content sync triggers."""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request

from src.config import get_settings
from src.database import async_session_factory
from src.github.client import GitHubClient
from src.services.sync_service import sync_from_github

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def _verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify the GitHub webhook HMAC-SHA256 signature.

    Args:
        payload: Raw request body bytes.
        signature: The X-Hub-Signature-256 header value.
        secret: The configured webhook secret.

    Returns:
        True if the signature is valid, False otherwise.
    """
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
) -> dict[str, str]:
    """Handle GitHub webhook events.

    Validates the HMAC-SHA256 signature, then dispatches based on
    event type. Currently handles push events to main, triggering
    a content sync.

    Args:
        request: The incoming HTTP request.
        db: Database session.
        x_hub_signature_256: GitHub's HMAC signature header.
        x_github_event: The event type header.

    Returns:
        A status message.

    Raises:
        HTTPException(400): If the signature is missing.
        HTTPException(401): If the signature is invalid.
    """
    settings = get_settings()
    payload = await request.body()

    # Validate signature
    if not x_hub_signature_256:
        raise HTTPException(status_code=400, detail="Missing signature")

    if not _verify_signature(payload, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Only process push events
    if x_github_event != "push":
        return {"status": "ignored", "reason": f"event type: {x_github_event}"}

    import json as json_lib

    body = json_lib.loads(payload)

    # Only sync on pushes to main
    if body.get("ref") != "refs/heads/main":
        return {"status": "ignored", "reason": "not main branch"}

    commit_sha = body.get("after", "unknown")
    logger.info("Webhook received: push to main (%s), starting sync", commit_sha)

    # Use a service-level token for sync (the webhook doesn't carry a user token)
    # In production, this should use a GitHub App installation token.
    github = GitHubClient(
        token=settings.github_client_secret,  # Placeholder — see note below
        repo_owner=settings.github_repo_owner,
        repo_name=settings.github_repo_name,
    )

    async with async_session_factory() as db:
        try:
            files_updated = await sync_from_github(db, github, commit_sha)
            logger.info("Sync completed: %d files updated", files_updated)
            return {"status": "synced", "files_updated": str(files_updated)}
        except Exception as exc:
            logger.exception("Sync failed for commit %s", commit_sha)
            raise HTTPException(status_code=500, detail="Sync failed") from exc
        finally:
            await github.close()
