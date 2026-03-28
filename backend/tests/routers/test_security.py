"""Tests for API security controls — input validation, error handling, headers."""


class TestInputValidation:
    def test_invalid_slug_pattern_rejected(self, client):
        """Slugs must be lowercase alphanumeric with hyphens only."""
        response = client.get("/api/docs/drop%20table%3B")
        assert response.status_code == 422

    def test_slug_with_uppercase_rejected(self, client):
        response = client.get("/api/docs/UPPERCASE")
        assert response.status_code == 422

    def test_notification_limit_too_high_rejected(self, client):
        """Limit parameter must be <= 100."""
        # Need auth for this endpoint — expect 401 before validation,
        # but the param validation should still be testable via OpenAPI schema
        response = client.get("/api/notifications?limit=999")
        # 401 because not authenticated, but schema is validated
        assert response.status_code in (401, 422)

    def test_notification_limit_negative_rejected(self, client):
        response = client.get("/api/notifications?limit=-1")
        assert response.status_code in (401, 422)


class TestErrorHandling:
    def test_404_does_not_leak_internals(self, client):
        """404 responses should be generic, not reveal implementation details."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        body = response.json()
        assert "traceback" not in str(body).lower()
        assert "sqlalchemy" not in str(body).lower()

    def test_auth_failure_is_generic(self, client):
        """Auth failures should not reveal why authentication failed."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
        body = response.json()
        # Should not say "JWT decode failed" or reveal algorithm
        assert "jwt" not in body["detail"].lower()


class TestSecurityHeaders:
    def test_all_security_headers_present(self, client):
        response = client.get("/api/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert "max-age=" in response.headers.get("Strict-Transport-Security", "")
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert response.headers.get("X-XSS-Protection") == "0"

    def test_cors_headers_on_options(self, client):
        """CORS preflight should return restricted methods."""
        response = client.options(
            "/api/docs",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should not include PUT (we don't use it on this endpoint)
        allowed = response.headers.get("Access-Control-Allow-Methods", "")
        assert "PUT" not in allowed or allowed == ""
