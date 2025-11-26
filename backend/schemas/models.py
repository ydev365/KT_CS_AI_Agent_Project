from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


# ============ Customer Schemas ============

class CustomerCreate(BaseModel):
    phone_number: str
    name: Optional[str] = None
    birth_date: Optional[date] = None


class CustomerResponse(BaseModel):
    id: int
    phone_number: str
    name: Optional[str]
    birth_date: Optional[date]
    is_kt_member: bool
    current_plan: Optional[str]
    subscription_date: Optional[date]

    class Config:
        from_attributes = True


# ============ Auth Schemas ============

class AuthRequest(BaseModel):
    phone_number: str


class AuthResponse(BaseModel):
    success: bool
    is_kt_member: bool
    customer: Optional[CustomerResponse]
    session_id: int
    greeting_message: str


# ============ Chat Schemas ============

class ChatMessageRequest(BaseModel):
    session_id: int
    message: str


class ChatMessageResponse(BaseModel):
    session_id: int
    user_message: str
    assistant_message: str
    requires_human_agent: bool = False


class ChatEndRequest(BaseModel):
    session_id: int


class ChatEndResponse(BaseModel):
    session_id: int
    summary: str
    message_count: int


# ============ STT Schemas ============

class STTResponse(BaseModel):
    success: bool
    transcribed_text: str
    error: Optional[str] = None


# ============ History Schemas ============

class MessageHistoryResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionHistoryResponse(BaseModel):
    id: int
    session_start: datetime
    session_end: Optional[datetime]
    summary: Optional[str]
    messages: List[MessageHistoryResponse] = []

    class Config:
        from_attributes = True
