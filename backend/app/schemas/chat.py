from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatSessionRequest(BaseModel):
    """상담 세션 생성 요청"""
    session_id: str = Field(..., description="인증 시 발급받은 세션 ID")


class ChatSessionResponse(BaseModel):
    """상담 세션 생성 응답"""
    session_id: str
    greeting: str = Field(..., description="AI 상담사 인사말")
    greeting_audio_base64: Optional[str] = Field(None, description="인사말 오디오 (Base64)")


class ChatMessageRequest(BaseModel):
    """메시지 전송 요청"""
    session_id: str
    message: str = Field(..., description="고객 메시지 텍스트")


class ChatMessageResponse(BaseModel):
    """메시지 응답"""
    session_id: str
    response: str = Field(..., description="AI 상담사 응답")
    response_audio_base64: Optional[str] = Field(None, description="응답 오디오 (Base64)")
    should_end: bool = Field(default=False, description="상담 종료 여부")
    plans_mentioned: Optional[List[str]] = Field(None, description="언급된 요금제 목록")


class ConversationMessage(BaseModel):
    """대화 메시지"""
    timestamp: str
    speaker: str  # "ai" or "customer"
    speaker_id: str
    content: str


class ConversationLog(BaseModel):
    """대화 로그"""
    session_id: str
    messages: List[ConversationMessage]
    start_time: str
    end_time: Optional[str] = None
