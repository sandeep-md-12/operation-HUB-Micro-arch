import pytest
from unittest.mock import AsyncMock

def test_health_endpoint(client):
    """Test the health check endpoint returns 200 OK and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_register_validation_error(client):
    """Test auth register returns 422 Unprocessable Entity when fields are missing."""
    response = client.post("/auth/register", json={})
    assert response.status_code == 422
