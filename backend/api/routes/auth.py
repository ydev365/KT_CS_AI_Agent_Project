from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from services.customer_service import CustomerService
from services.chat_service import ChatService
from schemas.models import AuthRequest, AuthResponse, CustomerResponse

router = APIRouter(prefix="/api/auth", tags=["인증"])


@router.post("/verify", response_model=AuthResponse)
def verify_customer(request: AuthRequest, db: Session = Depends(get_db)):
    """
    전화번호로 고객 인증
    - KT 회원이면 기존 정보 조회
    - 비회원이면 새로 등록
    - 새 상담 세션 생성
    """
    customer_service = CustomerService(db)
    chat_service = ChatService(db)

    # 고객 조회 또는 생성
    customer, is_new = customer_service.get_or_create_customer(request.phone_number)

    # 새 상담 세션 생성
    session = customer_service.create_chat_session(customer.id)

    # 인사말 생성
    greeting = chat_service.generate_greeting(customer, is_new)

    # 인사말을 세션에 저장
    chat_service.save_message(session.id, "assistant", greeting)

    return AuthResponse(
        success=True,
        is_kt_member=customer.is_kt_member,
        customer=CustomerResponse.model_validate(customer),
        session_id=session.id,
        greeting_message=greeting
    )
