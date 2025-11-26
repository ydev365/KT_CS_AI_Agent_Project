from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from services.chat_service import ChatService
from services.summary_service import SummaryService
from services.customer_service import CustomerService
from schemas.models import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatEndRequest,
    ChatEndResponse
)

router = APIRouter(prefix="/api/chat", tags=["채팅"])


@router.post("/message", response_model=ChatMessageResponse)
def send_message(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    채팅 메시지 전송 및 AI 응답 받기
    """
    # 세션 유효성 확인
    customer_service = CustomerService(db)
    session = customer_service.get_chat_session(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    if session.session_end:
        raise HTTPException(status_code=400, detail="이미 종료된 세션입니다.")

    # 메시지 처리
    chat_service = ChatService(db)
    assistant_message, requires_human = chat_service.process_message(
        request.session_id,
        request.message
    )

    return ChatMessageResponse(
        session_id=request.session_id,
        user_message=request.message,
        assistant_message=assistant_message,
        requires_human_agent=requires_human
    )


@router.post("/end", response_model=ChatEndResponse)
def end_chat(request: ChatEndRequest, db: Session = Depends(get_db)):
    """
    상담 종료 및 요약 생성
    """
    # 세션 유효성 확인
    customer_service = CustomerService(db)
    session = customer_service.get_chat_session(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    if session.session_end:
        raise HTTPException(status_code=400, detail="이미 종료된 세션입니다.")

    # 요약 생성 및 세션 종료
    summary_service = SummaryService(db)
    summary, message_count = summary_service.end_session_with_summary(request.session_id)

    return ChatEndResponse(
        session_id=request.session_id,
        summary=summary,
        message_count=message_count
    )
