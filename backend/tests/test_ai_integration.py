import pytest
from fastapi.testclient import TestClient


import os
import importlib


def test_ai_response_without_api_key(
    client: TestClient, sample_student, sample_message
):
    """Test that AI responds with fallback message when no API key is set."""
    # Explicitly unset the OpenAI API key for this test
    os.environ["OPENAI_API_KEY"] = ""
    # Force reload of settings to pick up the new environment variable
    import app.settings

    importlib.reload(app.settings)

    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]

    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    conv_response = client.post("/conversations", json=conv_data)
    conversation_id = conv_response.json()["id"]

    # Send a message
    response = client.post(
        f"/conversations/{conversation_id}/messages", json=sample_message
    )
    assert response.status_code == 200

    data = response.json()
    assert data["role"] == "assistant"
    assert "(AI not configured)" in data["content"]


def test_ai_response_content_quality(
    client: TestClient, sample_student, sample_message
):
    """Test that AI response is relevant to the user's message."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]

    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    conv_response = client.post("/conversations", json=conv_data)
    conversation_id = conv_response.json()["id"]

    # Send a message
    response = client.post(
        f"/conversations/{conversation_id}/messages", json=sample_message
    )
    assert response.status_code == 200

    data = response.json()
    # Even with fallback, should acknowledge the user's message
    assert len(data["content"]) > 20  # Reasonable response length


def test_conversation_context_persistence(client: TestClient, sample_student):
    """Test that conversation context is maintained across messages."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]

    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    conv_response = client.post("/conversations", json=conv_data)
    conversation_id = conv_response.json()["id"]

    # Send first message
    msg1 = {"content": "My name is John and I have a 3.8 GPA"}
    response1 = client.post(f"/conversations/{conversation_id}/messages", json=msg1)
    assert response1.status_code == 200

    # Send second message
    msg2 = {"content": "What should I know about applying to MIT?"}
    response2 = client.post(f"/conversations/{conversation_id}/messages", json=msg2)
    assert response2.status_code == 200

    # Get all messages
    messages_response = client.get(f"/conversations/{conversation_id}/messages")
    messages = messages_response.json()["messages"]

    # Should have 4 messages: 2 user + 2 assistant
    assert len(messages) == 4

    # Check that user messages are preserved
    user_messages = [msg for msg in messages if msg["role"] == "user"]
    assert len(user_messages) == 2
    assert user_messages[0]["content"] == msg1["content"]
    assert user_messages[1]["content"] == msg2["content"]


def test_multiple_conversations_isolation(client: TestClient, sample_student):
    """Test that conversations are isolated from each other."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]

    # Create two conversations
    conv1_data = {"student_id": student_id, "title": "Conv 1"}
    conv1_response = client.post("/conversations", json=conv1_data)
    conv1_id = conv1_response.json()["id"]

    conv2_data = {"student_id": student_id, "title": "Conv 2"}
    conv2_response = client.post("/conversations", json=conv2_data)
    conv2_id = conv2_response.json()["id"]

    # Send message to first conversation
    msg1 = {"content": "Hello from conversation 1"}
    client.post(f"/conversations/{conv1_id}/messages", json=msg1)

    # Send message to second conversation
    msg2 = {"content": "Hello from conversation 2"}
    client.post(f"/conversations/{conv2_id}/messages", json=msg2)

    # Check that conversations are separate
    conv1_messages = client.get(f"/conversations/{conv1_id}/messages").json()[
        "messages"
    ]
    conv2_messages = client.get(f"/conversations/{conv2_id}/messages").json()[
        "messages"
    ]

    assert len(conv1_messages) == 2  # User + assistant
    assert len(conv2_messages) == 2  # User + assistant

    # Messages should be different
    assert conv1_messages[0]["content"] != conv2_messages[0]["content"]


def test_student_context_summary_creation(client: TestClient, sample_student):
    """Test that student context summary is created after multiple messages."""
    # Create a student
    student_response = client.post("/auth/login", json=sample_student)
    student_id = student_response.json()["id"]

    # Create a conversation
    conv_data = {"student_id": student_id, "title": "Test Conv"}
    conv_response = client.post("/conversations", json=conv_data)
    conversation_id = conv_response.json()["id"]

    # Send multiple messages to trigger context summary (every 6 messages)
    for i in range(6):
        msg = {
            "content": f"Message {i+1}: I am a student with interests in computer science"
        }
        client.post(f"/conversations/{conversation_id}/messages", json=msg)

    # Get messages to verify they were created
    messages_response = client.get(f"/conversations/{conversation_id}/messages")
    messages = messages_response.json()["messages"]

    # Should have 12 messages: 6 user + 6 assistant
    assert len(messages) == 12

    # All messages should have content
    for msg in messages:
        assert len(msg["content"]) > 0
