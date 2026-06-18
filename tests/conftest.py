import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture(autouse=True, scope="session")
def mock_startup():
    """Mock database and AWS/DynamoDB initialization tasks on application startup."""
    with patch("app.utils.database.init_db", new_callable=AsyncMock) as mock_db, \
         patch("app.utils.dynamo.init_audit_log_table", new_callable=AsyncMock) as mock_dynamo, \
         patch("app.tasks.notification_tasks.listen_job_events.delay", new_callable=MagicMock) as mock_celery:
        yield mock_db, mock_dynamo, mock_celery


@pytest.fixture
def mock_db_session():
    """Fixture to provide a mocked SQLAlchemy AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def client(mock_db_session):
    """Fixture to provide a synchronous TestClient for testing endpoints."""
    from app.main import app
    from app.utils.database import get_db
    from fastapi.testclient import TestClient

    # Override get_db to return our mock session
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()
