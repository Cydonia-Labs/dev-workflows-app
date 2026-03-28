"""Tests for the authentication service."""

import os

import pytest

from src.services.auth_service import create_session_token, decode_session_token

# Ensure required env vars are set for tests
os.environ.setdefault("DATABASE_URL", "postgres://test:test@localhost:5432/test_db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("GITHUB_CLIENT_ID", "test")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test")
os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test")


class TestSessionTokens:
    def test_create_and_decode_roundtrip(self):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_session_token(user_id)
        payload = decode_session_token(token)
        assert payload["sub"] == user_id

    def test_decode_invalid_token_raises(self):
        with pytest.raises(Exception):
            decode_session_token("not-a-valid-jwt")

    def test_token_contains_expiry(self):
        token = create_session_token("some-user-id")
        payload = decode_session_token(token)
        assert "exp" in payload
        assert "iat" in payload
