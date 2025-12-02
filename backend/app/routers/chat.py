from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict

from ..schemas.chat import (
    ChatSessionRequest, ChatSessionResponse,
    ChatMessageRequest, ChatMessageResponse,
    ConversationLog, ConversationMessage
)
from ..schemas.auth import AuthResult
from ..services.session_service import session_service
from ..services.voice_service import voice_service
from ..agents.consultation_agent import ConsultationAgent

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 활성 에이전트 저장소
active_agents: Dict[str, ConsultationAgent] = {}


@router.post("/session", response_model=ChatSessionResponse)
async def create_chat_session(request: ChatSessionRequest):
    """
    AI 상담 세션 시작

    - 인증된 세션 ID로 상담 시작
    - AI 상담사 인사말 반환
    """
    print(f"[Chat] Creating session for: {request.session_id}")

    # 세션 확인
    session = session_service.get_session(request.session_id)
    if not session:
        print(f"[Chat] Session not found: {request.session_id}")
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다. 먼저 인증을 진행해주세요.")

    print(f"[Chat] Session found, status: {session.status}")

    if session.status == "ended":
        # 세션이 종료된 경우 다시 활성화
        print(f"[Chat] Reactivating ended session: {request.session_id}")
        session_service.update_session_status(request.session_id, "active")
        session.status = "active"
    elif session.status != "active":
        print(f"[Chat] Invalid session status: {session.status}")
        raise HTTPException(status_code=400, detail=f"세션 상태가 유효하지 않습니다: {session.status}")

    # AI 에이전트 생성
    agent = ConsultationAgent(session.customer_info)
    active_agents[request.session_id] = agent

    # 인사말 생성
    greeting = agent.generate_greeting()

    # 인사말 TTS
    try:
        greeting_audio = await voice_service.text_to_speech_base64(greeting)
    except Exception as e:
        print(f"TTS 오류: {e}")
        greeting_audio = None

    # 대화 기록 저장
    session_service.add_message(request.session_id, {
        "timestamp": datetime.now().isoformat(),
        "speaker": "ai",
        "speaker_id": "AI 상담사",
        "content": greeting
    })

    return ChatSessionResponse(
        session_id=request.session_id,
        greeting=greeting,
        greeting_audio_base64=greeting_audio
    )


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    메시지 전송 및 AI 응답

    - 고객 메시지를 AI에게 전달
    - AI 응답 및 음성 반환
    """
    # 에이전트 확인
    agent = active_agents.get(request.session_id)
    if not agent:
        raise HTTPException(status_code=404, detail="활성화된 상담 세션이 없습니다.")

    # 세션 확인
    session = session_service.get_session(request.session_id)
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="세션이 유효하지 않습니다.")

    # 고객 메시지 저장
    customer_name = session.customer_info.name or "고객"
    session_service.add_message(request.session_id, {
        "timestamp": datetime.now().isoformat(),
        "speaker": "customer",
        "speaker_id": f"고객_{session.customer_info.phone[-4:]}",
        "content": request.message
    })

    # AI 응답 생성
    try:
        response = await agent.process_message(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 응답 생성 중 오류: {str(e)}")

    # AI 응답 저장
    session_service.add_message(request.session_id, {
        "timestamp": datetime.now().isoformat(),
        "speaker": "ai",
        "speaker_id": "AI 상담사",
        "content": response.text
    })

    # 응답 TTS
    try:
        response_audio = await voice_service.text_to_speech_base64(response.text)
    except Exception as e:
        print(f"TTS 오류: {e}")
        response_audio = None

    # 상담 종료 처리
    if response.should_end:
        session_service.update_session_status(request.session_id, "ended")
        # 에이전트 제거
        del active_agents[request.session_id]

    return ChatMessageResponse(
        session_id=request.session_id,
        response=response.text,
        response_audio_base64=response_audio,
        should_end=response.should_end,
        plans_mentioned=response.plans_mentioned
    )


@router.get("/conversation/{session_id}", response_model=ConversationLog)
async def get_conversation(session_id: str):
    """대화 기록 조회"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    messages = session_service.get_conversation(session_id)

    return ConversationLog(
        session_id=session_id,
        messages=[ConversationMessage(**msg) for msg in messages],
        start_time=session.created_at,
        end_time=datetime.now().isoformat() if session.status == "ended" else None
    )


@router.delete("/session/{session_id}")
async def end_chat_session(session_id: str):
    """상담 세션 종료"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    # 세션 상태 업데이트
    session_service.update_session_status(session_id, "ended")

    # 에이전트 제거
    if session_id in active_agents:
        del active_agents[session_id]

    # 대화 기록 반환
    messages = session_service.get_conversation(session_id)

    return {
        "message": "상담이 종료되었습니다.",
        "session_id": session_id,
        "conversation": messages
    }
