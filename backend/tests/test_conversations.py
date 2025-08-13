import pytest
from fastapi.testclient import TestClient


def test_create_conversation(client: TestClient, sample_student):
    """Test creating a new conversation."""
    # First create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]
    
    # Create conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    response = client.post("/conversations", json=conv_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_id"] == student_id
    assert data["title"] == "Test Conv"
    assert "id" in data
    assert data["id"] > 0


def test_create_conversation_without_title(client: TestClient, sample_student):
    """Test creating a conversation without title uses default."""
    # First create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]
    
    # Create conversation without title
    conv_data = {"student_id": student_id}
    response = client.post("/conversations", json=conv_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "New Conversation"  # Default title


def test_create_conversation_invalid_student(client: TestClient):
    """Test creating conversation with non-existent student fails."""
    conv_data = {"student_id": 99999, "title": "Test"}
    response = client.post("/conversations", json=conv_data)
    assert response.status_code == 404
    assert "Student not found" in response.json()["detail"]


def test_list_conversations_empty(client: TestClient, sample_student):
    """Test listing conversations for new student returns empty list."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]
    
    # List conversations
    response = client.get(f"/conversations/{student_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["conversations"] == []


def test_list_conversations_with_data(client: TestClient, sample_student):
    """Test listing conversations returns created conversations."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]
    
    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Conv 1"}
    client.post("/conversations", json=conv_data)
    
    # Create another conversation
    conv_data2 = {"student_id": student_id, "title": "Conv 2"}
    client.post("/conversations", json=conv_data2)
    
    # List conversations
    response = client.get(f"/conversations/{student_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["conversations"]) == 2
    titles = [conv["title"] for conv in data["conversations"]]
    assert "Conv 1" in titles
    assert "Conv 2" in titles


def test_list_conversations_nonexistent_student(client: TestClient):
    """Test listing conversations for non-existent student returns empty."""
    response = client.get("/conversations/99999")
    assert response.status_code == 200
    
    data = response.json()
    assert data["conversations"] == []
