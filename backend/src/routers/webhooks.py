"""GitHub webhook handler and manual content sync triggers."""

import hashlib
import hmac
import json as json_lib
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import async_session_factory, get_db
from src.dependencies import get_current_user
from src.github.client import GitHubClient
from src.models.user import User
from src.services.sync_service import sync_from_github

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhooks"])

# Tracks commit SHAs whose syncs are currently scheduled or running, so
# GitHub retrying after its 10s delivery timeout doesn't kick off duplicate
# concurrent syncs. In-memory state — acceptable for the single-instance
# Railway deployment; would need Redis or a DB-backed lock for multi-instance.
_syncs_in_progress: set[str] = set()


async def _run_sync_in_background(commit_sha: str) -> None:
    """Run a content sync outside the request lifecycle.

    Opens its own DB session and GitHub client because the request scope
    is already torn down by the time FastAPI invokes this. Errors are
    logged rather than raised — there is no caller to return them to.

    Args:
        commit_sha: The commit SHA that triggered this sync.
    """
    settings = get_settings()
    github = GitHubClient(
        token=settings.github_seed_token,
        repo_owner=settings.github_repo_owner,
        repo_name=settings.github_repo_name,
    )

    try:
        async with async_session_factory() as db:
            files_updated = await sync_from_github(db, github, commit_sha)
            logger.info(
                "Background sync completed for %s: %d files updated",
                commit_sha,
                files_updated,
            )
    except Exception:
        logger.exception("Background sync failed for commit %s", commit_sha)
    finally:
        await github.close()
        _syncs_in_progress.discard(commit_sha)


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


@router.post("/api/webhooks/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
) -> dict[str, str]:
    """Handle GitHub webhook events.

    Validates the HMAC-SHA256 signature and filters by event type, then
    schedules a sync as a background task and returns immediately. GitHub
    webhook deliveries have a hard 10-second timeout; running the sync
    inline blew past that on any non-trivial doc set.

    Args:
        request: The incoming HTTP request.
        background_tasks: FastAPI scheduler for post-response work.
        x_hub_signature_256: GitHub's HMAC signature header.
        x_github_event: The event type header.

    Returns:
        A status message. "accepted" means a sync was scheduled,
        "in_progress" means one is already running for the same commit.

    Raises:
        HTTPException(400): If the signature is missing.
        HTTPException(401): If the signature is invalid.
    """
    settings = get_settings()
    payload = await request.body()

    if not x_hub_signature_256:
        raise HTTPException(status_code=400, detail="Missing signature")

    if not _verify_signature(payload, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    if x_github_event != "push":
        return {"status": "ignored", "reason": f"event type: {x_github_event}"}

    body = json_lib.loads(payload)

    if body.get("ref") != "refs/heads/main":
        return {"status": "ignored", "reason": "not main branch"}

    commit_sha = body.get("after", "unknown")

    # Dedupe against GitHub retries that fire while the previous sync is
    # still running (the original 10s-timeout scenario this fix addresses).
    if commit_sha in _syncs_in_progress:
        logger.info("Webhook received for %s but sync already in progress", commit_sha)
        return {"status": "in_progress", "commit": commit_sha}

    _syncs_in_progress.add(commit_sha)
    background_tasks.add_task(_run_sync_in_background, commit_sha)
    logger.info("Webhook received: push to main (%s), sync scheduled", commit_sha)
    return {"status": "accepted", "commit": commit_sha}


@router.post("/api/sync")
async def manual_resync(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Manually trigger a content sync from GitHub.

    Fetches the latest content from the dev-workflows repo and
    updates the database. Requires admin privileges.

    Args:
        user: The authenticated user (must be an admin).
        db: Database session.

    Returns:
        A status message with the number of files updated.

    Raises:
        HTTPException(403): If the user is not an admin.
        HTTPException(500): If the sync fails.
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    settings = get_settings()
    logger.info("Manual resync triggered by admin %s", user.github_login)

    github = GitHubClient(
        token=settings.github_seed_token,
        repo_owner=settings.github_repo_owner,
        repo_name=settings.github_repo_name,
    )

    try:
        files_updated = await sync_from_github(db, github, commit_sha="manual")
        logger.info("Manual sync completed: %d files updated", files_updated)
        return {"status": "synced", "files_updated": str(files_updated)}
    except Exception as exc:
        logger.exception("Manual sync failed")
        raise HTTPException(status_code=500, detail="Sync failed") from exc
    finally:
        await github.close()
