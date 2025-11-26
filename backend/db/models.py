from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Customer(Base):
    """고객 테이블"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=True)
    is_kt_member = Column(Boolean, default=False)
    current_plan = Column(String(100), nullable=True)
    subscription_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="customer")


class ChatSession(Base):
    """상담 이력 테이블"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    session_start = Column(DateTime, server_default=func.now())
    session_end = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """채팅 메시지 테이블"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
