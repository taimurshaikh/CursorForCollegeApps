from __future__ import annotations

from typing import List, Dict
from sqlalchemy.orm import Session
from openai import OpenAI

from app.settings import Settings
from app import models


def _fallback_reply(
    history_messages: List[Dict[str, str]], student_context_summary: str | None
) -> str:
    last_user = next(
        (m for m in reversed(history_messages) if m.get("role") == "user"), None
    )
    prefix = "(AI not configured) "
    if last_user:
        return f"{prefix}I hear you: '{last_user.get('content','')[:300]}'. While AI is disabled, I can still help structure your next steps. Could you share your GPA, intended majors, and any target schools?"
    return f"{prefix}Hi! While AI is disabled, I can still help organize your plan. Tell me about your academics, activities, and goals."


def generate_assistant_reply(
    history_messages: List[Dict[str, str]], student_context_summary: str | None
) -> str:
    # Instantiate fresh settings each call to pick up latest .env/ENV
    settings = Settings()

    if not settings.openai_api_key:
        return _fallback_reply(history_messages, student_context_summary)

    messages: List[Dict[str, str]] = []
    system_content = (
        "You are a helpful AI college counseling assistant. "
        "Be concise, actionable, and supportive. "
        "Use the student's saved context when relevant."
    )
    if student_context_summary:
        system_content += (
            "\n\nStudent context summary (may be incomplete, do not assume facts not present):\n"
            + student_context_summary
        )

    messages.append({"role": "system", "content": system_content})
    messages.extend(history_messages)

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        completion = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
        )
        return completion.choices[0].message.content or ""
    except Exception:
        return _fallback_reply(history_messages, student_context_summary)


def summarize_student_context(db: Session, student_id: int) -> str:
    # Fetch previous summary
    prev_summary: str = ""
    student_ctx = (
        db.query(models.StudentContext)
        .filter(models.StudentContext.student_id == student_id)
        .one_or_none()
    )
    if student_ctx and student_ctx.context_summary:
        prev_summary = student_ctx.context_summary

    # Fetch last 100 messages across all conversations for this student
    messages = (
        db.query(models.Message)
        .join(
            models.Conversation,
            models.Message.conversation_id == models.Conversation.id,
        )
        .filter(models.Conversation.student_id == student_id)
        .order_by(models.Message.created_at.desc())
        .limit(100)
        .all()
    )

    ordered = list(reversed(messages))
    history: List[Dict[str, str]] = [
        {"role": m.role, "content": m.content} for m in ordered
    ]

    prompt_messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are updating a student's persistent profile for a college counseling assistant. "
                "Summarize key facts only (academics, activities, preferences, constraints, goals). "
                "Keep it under 180 words. If information is unclear, omit it."
            ),
        },
    ]
    if prev_summary:
        prompt_messages.append(
            {
                "role": "system",
                "content": "Previous summary (may be outdated):\n" + prev_summary,
            }
        )
    prompt_messages.extend(history)

    summary = generate_assistant_reply(prompt_messages[1:], prev_summary)

    if student_ctx is None:
        student_ctx = models.StudentContext(
            student_id=student_id, context_summary=summary
        )
        db.add(student_ctx)
    else:
        student_ctx.context_summary = summary

    db.commit()
    return summary
