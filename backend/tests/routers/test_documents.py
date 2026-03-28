"""Tests for document endpoints.

Note: Endpoints that hit the database via async SQLAlchemy/asyncpg
require proper async test infrastructure with migrations applied.
These tests verify route registration via the OpenAPI schema
rather than making live DB requests.
"""


def test_docs_endpoints_registered(client):
    """Verify document endpoints are present in the OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/docs" in paths
    assert "/api/docs/{slug}" in paths
    assert "/api/docs/{slug}/sections/{anchor}" in paths
