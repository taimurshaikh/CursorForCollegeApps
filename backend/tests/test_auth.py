import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns status ok."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_new_student(client: TestClient, sample_student):
    """Test logging in with a new student creates the student."""
    response = client.post("/auth/login", json=sample_student)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == sample_student["email"]
    assert data["name"] == sample_student["name"]
    assert "id" in data
    assert data["id"] > 0


def test_login_existing_student(client: TestClient, sample_student):
    """Test logging in with an existing student returns the same student."""
    # First login
    response1 = client.post("/auth/login", json=sample_student)
    assert response1.status_code == 200
    student_id1 = response1.json()["id"]
    
    # Second login with same email
    response2 = client.post("/auth/login", json=sample_student)
    assert response2.status_code == 200
    student_id2 = response2.json()["id"]
    
    # Should return the same student ID
    assert student_id1 == student_id2


def test_login_without_name(client: TestClient):
    """Test logging in without a name uses default name."""
    login_data = {"email": "no-name@example.com"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == login_data["email"]
    assert data["name"] == "Student"  # Default name


def test_login_invalid_email(client: TestClient):
    """Test login with invalid email format."""
    login_data = {"email": "invalid-email", "name": "Test"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 422  # Validation error


def test_login_missing_email(client: TestClient):
    """Test login without email returns validation error."""
    login_data = {"name": "Test Student"}
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 422  # Validation error
