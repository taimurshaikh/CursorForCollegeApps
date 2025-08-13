from __future__ import annotations

from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db import Base, engine, SessionLocal, get_db
from app import models
from app.schemas import (
    LoginRequest,
    StudentOut,
    ConversationCreate,
    ConversationOut,
    MessageCreate,
    MessageOut,
    MessagesResponse,
    ConversationsResponse,
)
from app.ai import generate_assistant_reply, summarize_student_context

app = FastAPI(title="College Counseling AI - Cupcake")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.post("/auth/login", response_model=StudentOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    student = (
        db.query(models.Student)
        .filter(models.Student.email == payload.email)
        .one_or_none()
    )
    if student is None:
        student = models.Student(email=payload.email, name=payload.name or "Student")
        db.add(student)
        db.commit()
        db.refresh(student)
    return student


@app.get("/conversations/{student_id}", response_model=ConversationsResponse)
def list_conversations(student_id: int, db: Session = Depends(get_db)):
    convos = (
        db.query(models.Conversation)
        .filter(models.Conversation.student_id == student_id)
        .order_by(models.Conversation.created_at.desc())
        .all()
    )
    return {"conversations": convos}


@app.post("/conversations", response_model=ConversationOut)
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db)):
    student = (
        db.query(models.Student)
        .filter(models.Student.id == payload.student_id)
        .one_or_none()
    )
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    title = payload.title or "New Conversation"
    conv = models.Conversation(student_id=payload.student_id, title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@app.get("/conversations/{conversation_id}/messages", response_model=MessagesResponse)
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    conv = (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id)
        .one_or_none()
    )
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )
    return {"messages": msgs}


@app.post("/conversations/{conversation_id}/messages", response_model=MessageOut)
def send_message(
    conversation_id: int, payload: MessageCreate, db: Session = Depends(get_db)
):
    conv = (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id)
        .one_or_none()
    )
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Store user message
    user_msg = models.Message(
        conversation_id=conversation_id, role="user", content=payload.content
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Fetch recent history for prompt
    recent_msgs = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at.asc())
        .limit(30)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in recent_msgs]

    # Load student context
    ctx = (
        db.query(models.StudentContext)
        .filter(models.StudentContext.student_id == conv.student_id)
        .one_or_none()
    )
    ctx_summary = ctx.context_summary if ctx else None

    assistant_text = generate_assistant_reply(history, ctx_summary)

    assistant_msg = models.Message(
        conversation_id=conversation_id, role="assistant", content=assistant_text
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # Periodically update student context (every 6 messages total for this student)
    total_messages = (
        db.query(func.count(models.Message.id))
        .join(
            models.Conversation,
            models.Message.conversation_id == models.Conversation.id,
        )
        .filter(models.Conversation.student_id == conv.student_id)
        .scalar()
    )
    if total_messages and total_messages % 6 == 0:
        try:
            summarize_student_context(db, conv.student_id)
        except Exception:
            pass

    return assistant_msg


# Simple root
@app.get("/")
def root():
    return {"status": "ok"}
