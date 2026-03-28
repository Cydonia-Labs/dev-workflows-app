"""Shared test fixtures for the backend test suite."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Provide a FastAPI test client for integration tests."""
    with TestClient(app) as test_client:
        yield test_client
