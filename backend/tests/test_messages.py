import pytest
from fastapi.testclient import TestClient


def test_send_message(client: TestClient, sample_student, sample_message):
    """Test sending a message creates both user and assistant messages."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]
    
    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    conv_response = client.post("/conversations", json=conv_data)
    conversation_id = conv_response.json()["id"]
    
    # Send a message
    response = client.post(f"/conversations/{conversation_id}/messages", json=sample_message)
    assert response.status_code == 200
    
    data = response.json()
    assert data["conversation_id"] == conversation_id
    assert data["role"] == "assistant"
    assert len(data["content"]) > 0


def test_get_messages_empty_conversation(client: TestClient, sample_student):
    """Test getting messages from empty conversation returns empty list."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]
    
    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    conv_response = client.post("/conversations", json=conv_data)
    conversation_id = conv_response.json()["id"]
    
    # Get messages
    response = client.get(f"/conversations/{conversation_id}/messages")
    assert response.status_code == 200
    
    data = response.json()
    assert data["messages"] == []


def test_get_messages_with_data(client: TestClient, sample_student, sample_message):
    """Test getting messages returns all messages in conversation."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]
    
    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    conv_response = client.post("/conversations", json=conv_data)
    conversation_id = conv_response.json()["id"]
    
    # Send a message
    client.post(f"/conversations/{conversation_id}/messages", json=sample_message)
    
    # Get messages
    response = client.get(f"/conversations/{conversation_id}/messages")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["messages"]) == 2  # User message + assistant response
    
    # Check user message
    user_msg = next(msg for msg in data["messages"] if msg["role"] == "user")
    assert user_msg["content"] == sample_message["content"]
    assert user_msg["conversation_id"] == conversation_id
    
    # Check assistant message
    assistant_msg = next(msg for msg in data["messages"] if msg["role"] == "assistant")
    assert assistant_msg["role"] == "assistant"
    assert len(assistant_msg["content"]) > 0


def test_send_message_nonexistent_conversation(client: TestClient, sample_message):
    """Test sending message to non-existent conversation fails."""
    response = client.post("/conversations/99999/messages", json=sample_message)
    assert response.status_code == 404
    assert "Conversation not found" in response.json()["detail"]


def test_get_messages_nonexistent_conversation(client: TestClient):
    """Test getting messages from non-existent conversation fails."""
    response = client.get("/conversations/99999/messages")
    assert response.status_code == 404
    assert "Conversation not found" in response.json()["detail"]


def test_message_persistence(client: TestClient, sample_student, sample_message):
    """Test that messages persist and can be retrieved."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]
    
    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    conv_response = client.post("/conversations", json=conv_data)
    conversation_id = conv_response.json()["id"]
    
    # Send a message
    client.post(f"/conversations/{conversation_id}/messages", json=sample_message)
    
    # Get messages immediately
    response1 = client.get(f"/conversations/{conversation_id}/messages")
    messages1 = response1.json()["messages"]
    
    # Get messages again
    response2 = client.get(f"/conversations/{conversation_id}/messages")
    messages2 = response2.json()["messages"]
    
    # Should be identical
    assert len(messages1) == len(messages2)
    assert messages1 == messages2
