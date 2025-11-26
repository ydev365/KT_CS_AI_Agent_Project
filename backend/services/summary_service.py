from openai import OpenAI
from sqlalchemy.orm import Session
from typing import Optional
from db.models import ChatMessage, ChatSession
from config import get_settings

settings = get_settings()

SUMMARY_PROMPT = """다음은 KT 요금제 상담 대화 내용입니다. 이 대화를 간결하게 요약해주세요.

요약에 포함할 내용:
1. 고객의 주요 문의 사항
2. 상담원이 제공한 주요 정보/추천 내용
3. 상담 결과 (해결 여부, 추가 조치 필요 여부)

요약은 3-5문장으로 작성해주세요.
"""


class SummaryService:
    """대화 요약 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)

    def get_session_messages(self, session_id: int) -> list:
        """세션의 모든 메시지 조회"""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        return messages

    def format_conversation(self, messages: list) -> str:
        """대화 내용을 텍스트로 포맷"""
        conversation_parts = []
        for msg in messages:
            role_name = "고객" if msg.role == "user" else "상담원"
            conversation_parts.append(f"{role_name}: {msg.content}")
        return "\n".join(conversation_parts)

    def generate_summary(self, session_id: int) -> Optional[str]:
        """대화 요약 생성"""
        messages = self.get_session_messages(session_id)

        if not messages:
            return "상담 내용이 없습니다."

        if len(messages) < 2:
            return "상담이 충분히 진행되지 않았습니다."

        conversation = self.format_conversation(messages)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SUMMARY_PROMPT},
                    {"role": "user", "content": f"대화 내용:\n{conversation}"}
                ],
                temperature=0.5,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"요약 생성 중 오류 발생: {str(e)}"

    def end_session_with_summary(self, session_id: int) -> tuple:
        """세션 종료 및 요약 저장"""
        from datetime import datetime

        # 요약 생성
        summary = self.generate_summary(session_id)

        # 세션 업데이트
        session = self.db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()

        if session:
            session.session_end = datetime.now()
            session.summary = summary
            self.db.commit()

            # 메시지 수 계산
            message_count = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).count()

            return summary, message_count

        return summary, 0
