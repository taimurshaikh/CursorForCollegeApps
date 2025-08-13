import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.db import Base, get_db


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Create a test client with test database."""
    return TestClient(app)


@pytest.fixture
def sample_student():
    """Sample student data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test Student"
    }


@pytest.fixture
def sample_conversation():
    """Sample conversation data for testing."""
    return {
        "title": "Test Conversation"
    }


@pytest.fixture
def sample_message():
    """Sample message data for testing."""
    return {
        "content": "Hello, this is a test message!"
    }
