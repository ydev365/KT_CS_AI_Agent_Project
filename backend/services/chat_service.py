from openai import OpenAI
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from db.models import ChatMessage, ChatSession, Customer
from services.rag_service import RAGService
from config import get_settings

settings = get_settings()

# 상담원 연결 키워드
HUMAN_AGENT_KEYWORDS = [
    "상담원 연결", "상담원", "상담사", "사람", "직원", "실제 상담",
    "사람과 통화", "상담원 연결해줘", "상담원이랑", "담당자"
]

# AI가 처리할 수 없는 문의 키워드
ESCALATION_KEYWORDS = [
    "명의 변경", "명의변경", "요금 납부", "요금납부", "분실 신고", "분실신고",
    "해지", "번호 변경", "번호변경", "기기 변경", "기기변경", "A/S", "수리",
    "청구서", "미납", "연체", "위약금", "계약 해지"
]

SYSTEM_PROMPT = """당신은 KT 요금제 전문 AI 상담원입니다.

[역할]
- KT 5G/LTE 요금제에 대한 상담 및 추천
- 고객의 사용 패턴에 맞는 최적의 요금제 안내

[상담 가이드라인]
1. 고객에게 필요한 정보를 적극적으로 질문하세요
   - "월 평균 데이터 사용량이 어떻게 되시나요?"
   - "주로 어떤 용도로 데이터를 사용하시나요?"
   - "데이터 이월 기능이 필요하신가요?"

2. 고객 정보를 활용한 맞춤 추천
   - 현재 요금제 대비 절약 가능 금액 안내
   - 고객 나이에 맞는 연령별 요금제 안내 (Y, Y틴, 주니어, 시니어 등)

3. 요금제 외 문의 또는 해결 불가 시
   - "해당 문의는 전문 상담원 연결이 필요합니다. 상담원 연결을 원하시면 '상담원 연결'이라고 말씀해 주세요."
   - 명의 변경, 요금 납부, 분실 신고 등은 상담원 연결 안내

4. 항상 친절하고 전문적인 어조를 유지하세요.
5. 답변은 간결하고 명확하게 해주세요.
"""


class ChatService:
    """LLM 채팅 처리 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.rag_service = RAGService()

    def generate_greeting(self, customer: Customer, is_new: bool) -> str:
        """인사말 생성"""
        greeting = "안녕하세요, KT AI 상담원입니다. 요금제 관련 상담을 도와드리겠습니다.\n"
        greeting += "상담 중 언제든지 '상담원 연결'이라고 말씀하시면 전문 상담원과 연결해 드립니다.\n\n"

        if customer.is_kt_member:
            greeting += f"{customer.name or '고객'}님, KT를 이용해 주셔서 감사합니다.\n"
            if customer.current_plan:
                greeting += f"현재 사용 중이신 요금제는 '{customer.current_plan}'입니다.\n"
            greeting += "\n무엇을 도와드릴까요?"
        else:
            greeting += "KT 요금제에 대해 궁금하신 점을 말씀해 주세요.\n"
            greeting += "고객님께 맞는 요금제를 안내해 드리겠습니다."

        return greeting

    def check_requires_human_agent(self, message: str) -> Tuple[bool, Optional[str]]:
        """상담원 연결 필요 여부 확인"""
        message_lower = message.lower()

        # 상담원 연결 직접 요청
        for keyword in HUMAN_AGENT_KEYWORDS:
            if keyword in message_lower:
                return True, "상담원 연결을 요청하셨습니다. 잠시 후 전문 상담원과 연결해 드리겠습니다. 감사합니다."

        # AI가 처리할 수 없는 문의
        for keyword in ESCALATION_KEYWORDS:
            if keyword in message_lower:
                return True, f"'{keyword}' 관련 문의는 전문 상담원의 도움이 필요합니다. 상담원 연결을 원하시면 '상담원 연결'이라고 말씀해 주세요."

        return False, None

    def get_chat_history(self, session_id: int, limit: int = 10) -> list:
        """최근 대화 기록 조회"""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]

    def save_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        """메시지 저장"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_customer_context(self, session_id: int) -> str:
        """고객 정보 컨텍스트 생성"""
        session = self.db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()

        if not session or not session.customer:
            return ""

        customer = session.customer
        context_parts = ["[고객 정보]"]

        if customer.name:
            context_parts.append(f"- 이름: {customer.name}")

        if customer.is_kt_member:
            context_parts.append("- KT 회원: 예")
            if customer.current_plan:
                context_parts.append(f"- 현재 요금제: {customer.current_plan}")
            if customer.subscription_date:
                context_parts.append(f"- 가입일: {customer.subscription_date}")
        else:
            context_parts.append("- KT 회원: 아니오 (잠재 고객)")

        if customer.birth_date:
            from datetime import datetime
            today = datetime.now().date()
            age = today.year - customer.birth_date.year
            if (today.month, today.day) < (customer.birth_date.month, customer.birth_date.day):
                age -= 1
            context_parts.append(f"- 나이: {age}세")

            # 연령별 요금제 추천 힌트
            if age <= 12:
                context_parts.append("- 추천 대상: 5G 주니어 요금제 (만 12세 이하)")
            elif age <= 18:
                context_parts.append("- 추천 대상: 5G Y틴 요금제 (만 18세 이하)")
            elif age <= 34:
                context_parts.append("- 추천 대상: 5G Y 요금제 (만 34세 이하)")
            elif age >= 65:
                context_parts.append("- 추천 대상: 5G 시니어 요금제 (만 65세 이상)")

        return "\n".join(context_parts)

    def process_message(self, session_id: int, user_message: str) -> Tuple[str, bool]:
        """
        사용자 메시지 처리
        Returns: (assistant_response, requires_human_agent)
        """
        # 상담원 연결 필요 여부 확인
        requires_human, escalation_msg = self.check_requires_human_agent(user_message)
        if requires_human and escalation_msg:
            self.save_message(session_id, "user", user_message)
            self.save_message(session_id, "assistant", escalation_msg)
            return escalation_msg, True

        # 사용자 메시지 저장
        self.save_message(session_id, "user", user_message)

        # RAG 컨텍스트 가져오기
        rag_context = self.rag_service.get_context_for_query(user_message)

        # 고객 정보 컨텍스트
        customer_context = self.get_customer_context(session_id)

        # 대화 기록 가져오기
        chat_history = self.get_chat_history(session_id)

        # 메시지 구성
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"{customer_context}\n\n{rag_context}"}
        ]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        # GPT 호출
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        assistant_message = response.choices[0].message.content

        # 어시스턴트 메시지 저장
        self.save_message(session_id, "assistant", assistant_message)

        return assistant_message, False
