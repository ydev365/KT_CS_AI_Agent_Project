from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from services.customer_service import CustomerService
from schemas.models import SessionHistoryResponse, MessageHistoryResponse

router = APIRouter(prefix="/api/history", tags=["상담 이력"])


@router.get("/{phone_number}", response_model=List[SessionHistoryResponse])
def get_customer_history(phone_number: str, db: Session = Depends(get_db)):
    """
    고객의 상담 이력 조회 (전화번호로)
    """
    customer_service = CustomerService(db)
    sessions = customer_service.get_customer_sessions(phone_number)

    if not sessions:
        return []

    return [
        SessionHistoryResponse(
            id=session.id,
            session_start=session.session_start,
            session_end=session.session_end,
            summary=session.summary,
            messages=[]  # 목록에서는 메시지 미포함
        )
        for session in sessions
    ]


@router.get("/session/{session_id}", response_model=SessionHistoryResponse)
def get_session_detail(session_id: int, db: Session = Depends(get_db)):
    """
    특정 상담 세션 상세 조회 (메시지 포함)
    """
    customer_service = CustomerService(db)
    session = customer_service.get_chat_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    return SessionHistoryResponse(
        id=session.id,
        session_start=session.session_start,
        session_end=session.session_end,
        summary=session.summary,
        messages=[
            MessageHistoryResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in session.messages
        ]
    )
