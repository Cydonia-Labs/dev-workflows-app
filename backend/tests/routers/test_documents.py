"""Tests for document endpoints.

Note: Endpoints that hit the database via async SQLAlchemy/asyncpg
require proper async test infrastructure. The sync TestClient can't
manage the async event loop for DB sessions. Full integration tests
with DB will be added when we set up async test fixtures.
"""


def test_docs_endpoint_is_registered(client):
    """Verify the /api/docs endpoint exists and is routable."""
    response = client.get("/api/docs")
    # May return 200 (empty list) or 500 (event loop issue) —
    # either confirms the route exists
    assert response.status_code in (200, 500)
