from sqlalchemy.orm import Session
from typing import Optional, Tuple
from db.models import Customer, ChatSession
from datetime import datetime


class CustomerService:
    """고객 DB 조회 및 관리 서비스"""

    def __init__(self, db: Session):
        self.db = db

    def get_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        """전화번호로 고객 조회"""
        return self.db.query(Customer).filter(
            Customer.phone_number == phone_number
        ).first()

    def create_customer(self, phone_number: str, name: Optional[str] = None) -> Customer:
        """새 고객 생성 (비회원)"""
        customer = Customer(
            phone_number=phone_number,
            name=name,
            is_kt_member=False
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_or_create_customer(self, phone_number: str) -> Tuple[Customer, bool]:
        """
        고객 조회 또는 생성
        Returns: (customer, is_new)
        """
        customer = self.get_customer_by_phone(phone_number)
        if customer:
            return customer, False
        return self.create_customer(phone_number), True

    def create_chat_session(self, customer_id: int) -> ChatSession:
        """새 상담 세션 생성"""
        session = ChatSession(customer_id=customer_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def end_chat_session(self, session_id: int, summary: str) -> Optional[ChatSession]:
        """상담 세션 종료"""
        session = self.db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        if session:
            session.session_end = datetime.now()
            session.summary = summary
            self.db.commit()
            self.db.refresh(session)
        return session

    def get_chat_session(self, session_id: int) -> Optional[ChatSession]:
        """세션 ID로 상담 세션 조회"""
        return self.db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()

    def get_customer_sessions(self, phone_number: str) -> list:
        """고객의 모든 상담 세션 조회"""
        customer = self.get_customer_by_phone(phone_number)
        if not customer:
            return []
        return self.db.query(ChatSession).filter(
            ChatSession.customer_id == customer.id
        ).order_by(ChatSession.session_start.desc()).all()

    def calculate_age(self, customer: Customer) -> Optional[int]:
        """고객 나이 계산"""
        if not customer.birth_date:
            return None
        today = datetime.now().date()
        age = today.year - customer.birth_date.year
        if (today.month, today.day) < (customer.birth_date.month, customer.birth_date.day):
            age -= 1
        return age
