"""Tests for the webhook endpoint."""

import hashlib
import hmac
import json
import os

from src.routers import webhooks

# Must match the GITHUB_WEBHOOK_SECRET set in conftest.py
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "test-webhook-secret")


def _sign_payload(payload: bytes) -> str:
    """Generate a GitHub-style HMAC-SHA256 signature.

    Args:
        payload: The raw request body.

    Returns:
        The signature string in sha256=<hex> format.
    """
    return "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()


def test_webhook_rejects_missing_signature(client):
    response = client.post("/api/webhooks/github", content=b"{}")
    assert response.status_code == 400


def test_webhook_rejects_invalid_signature(client):
    response = client.post(
        "/api/webhooks/github",
        content=b"{}",
        headers={
            "X-Hub-Signature-256": "sha256=invalid",
            "X-GitHub-Event": "push",
        },
    )
    assert response.status_code == 401


def test_webhook_ignores_non_push_events(client):
    payload = b'{"action": "opened"}'
    response = client.post(
        "/api/webhooks/github",
        content=payload,
        headers={
            "X-Hub-Signature-256": _sign_payload(payload),
            "X-GitHub-Event": "pull_request",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"


def test_webhook_ignores_non_main_branch(client):
    body = {"ref": "refs/heads/feature/test", "after": "abc123"}
    payload = json.dumps(body).encode()
    response = client.post(
        "/api/webhooks/github",
        content=payload,
        headers={
            "X-Hub-Signature-256": _sign_payload(payload),
            "X-GitHub-Event": "push",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"


def test_webhook_push_to_main_schedules_background_sync(client, monkeypatch):
    """Push to main returns 'accepted' immediately and schedules the sync."""
    scheduled: list[str] = []

    async def fake_sync(commit_sha: str) -> None:
        scheduled.append(commit_sha)

    monkeypatch.setattr(webhooks, "_run_sync_in_background", fake_sync)
    webhooks._syncs_in_progress.clear()

    body = {"ref": "refs/heads/main", "after": "deadbeef"}
    payload = json.dumps(body).encode()
    response = client.post(
        "/api/webhooks/github",
        content=payload,
        headers={
            "X-Hub-Signature-256": _sign_payload(payload),
            "X-GitHub-Event": "push",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "accepted", "commit": "deadbeef"}
    # BackgroundTasks run after the response is returned by TestClient,
    # so the fake should have been invoked by now.
    assert scheduled == ["deadbeef"]


def test_webhook_dedupes_concurrent_sync_for_same_commit(client, monkeypatch):
    """A second delivery for the same commit while sync is running returns 'in_progress'."""

    async def fake_sync(commit_sha: str) -> None:
        # Intentionally does nothing — we want the in-progress set to stay
        # populated for the duration of the test (we pre-populate it below).
        pass

    monkeypatch.setattr(webhooks, "_run_sync_in_background", fake_sync)
    webhooks._syncs_in_progress.clear()
    webhooks._syncs_in_progress.add("deadbeef")

    body = {"ref": "refs/heads/main", "after": "deadbeef"}
    payload = json.dumps(body).encode()
    response = client.post(
        "/api/webhooks/github",
        content=payload,
        headers={
            "X-Hub-Signature-256": _sign_payload(payload),
            "X-GitHub-Event": "push",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "in_progress", "commit": "deadbeef"}

    webhooks._syncs_in_progress.clear()
