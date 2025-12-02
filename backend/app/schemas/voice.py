from pydantic import BaseModel, Field
from typing import Optional


class TTSRequest(BaseModel):
    """TTS 요청"""
    text: str = Field(..., description="음성으로 변환할 텍스트")
    voice: Optional[str] = Field(default="nova", description="음성 종류 (alloy, echo, fable, onyx, nova, shimmer)")


class TTSResponse(BaseModel):
    """TTS 응답"""
    audio_base64: str = Field(..., description="Base64 인코딩된 오디오 데이터")
    content_type: str = Field(default="audio/mpeg", description="오디오 MIME 타입")


class STTResponse(BaseModel):
    """STT 응답"""
    text: str = Field(..., description="인식된 텍스트")
    language: str = Field(default="ko", description="인식된 언어")
