"""Shared test fixtures for the backend test suite."""

import os

# Set test environment variables before any app imports
os.environ.setdefault("DATABASE_URL", "postgres://devuser:devpass@localhost:5432/dev_workflows")
os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-chars!!")
os.environ.setdefault("GITHUB_CLIENT_ID", "test-client-id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-webhook-secret")
os.environ.setdefault("GITHUB_REPO_OWNER", "test-owner")
os.environ.setdefault("GITHUB_REPO_NAME", "test-repo")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Provide a FastAPI test client for integration tests."""
    with TestClient(app) as test_client:
        yield test_client
