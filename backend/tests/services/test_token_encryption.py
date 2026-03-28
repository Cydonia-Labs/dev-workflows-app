"""Tests for token encryption service."""

import pytest

from src.services.token_encryption import decrypt_token, encrypt_token


class TestTokenEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        secret = "test-secret-key-minimum-32-chars!!"
        plaintext = "ghp_abc123XYZ789tokensecret"
        encrypted = encrypt_token(plaintext, secret)
        assert encrypted != plaintext
        assert decrypt_token(encrypted, secret) == plaintext

    def test_different_secrets_produce_different_ciphertexts(self):
        plaintext = "ghp_abc123"
        enc1 = encrypt_token(plaintext, "secret-key-one-minimum-32-chars!")
        enc2 = encrypt_token(plaintext, "secret-key-two-minimum-32-chars!")
        assert enc1 != enc2

    def test_wrong_secret_fails_decryption(self):
        encrypted = encrypt_token("ghp_abc123", "correct-key-minimum-32-characters!")
        with pytest.raises(Exception):
            decrypt_token(encrypted, "wrong-key-minimum-32-characters!!")

    def test_same_secret_produces_different_ciphertexts(self):
        """Fernet includes a timestamp, so identical inputs produce different outputs."""
        secret = "test-secret-key-minimum-32-chars!!"
        enc1 = encrypt_token("ghp_abc123", secret)
        enc2 = encrypt_token("ghp_abc123", secret)
        assert enc1 != enc2  # Different due to Fernet's IV/timestamp

    def test_empty_token(self):
        secret = "test-secret-key-minimum-32-chars!!"
        encrypted = encrypt_token("", secret)
        assert decrypt_token(encrypted, secret) == ""


class TestRateLimitMiddleware:
    def test_health_check_not_rate_limited(self, client):
        """Health check should be exempt from rate limiting."""
        for _ in range(150):
            response = client.get("/api/health")
            assert response.status_code == 200

    def test_responses_have_security_headers(self, client):
        """All responses should include security headers."""
        response = client.get("/api/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
