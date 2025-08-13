from typing import Optional, List, Literal
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class StudentOut(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    student_id: int
    title: Optional[str] = None


class ConversationOut(BaseModel):
    id: int
    student_id: int
    title: str

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    role: Literal["user", "assistant"]
    content: str

    class Config:
        from_attributes = True


class MessagesResponse(BaseModel):
    messages: List[MessageOut]


class ConversationsResponse(BaseModel):
    conversations: List[ConversationOut]
