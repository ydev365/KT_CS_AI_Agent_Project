from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel

from ..core.config import settings


class ConversationSummary(BaseModel):
    """대화 요약"""
    current_plan: str
    current_price: int
    requested_feature: str
    customer_profile: str
    main_concern: str
    opportunity: str
    consultation_result: str  # 상담 결과 (고객이 선택한 요금제/서비스)


class SummaryService:
    """대화 요약 서비스"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def summarize_conversation(
        self,
        conversation: List[Dict[str, Any]],
        customer_info: Dict[str, Any]
    ) -> ConversationSummary:
        """
        상담 대화 요약 생성

        Args:
            conversation: 대화 기록 리스트
            customer_info: 고객 정보

        Returns:
            대화 요약
        """
        # 대화 내용 포맷팅
        conversation_text = self._format_conversation(conversation)

        # 요약 프롬프트
        # None 값 처리
        monthly_fee = customer_info.get('monthly_fee') or 0

        prompt = f"""다음 KT 고객센터 AI 상담 대화를 분석하여 요약해주세요.

## 고객 정보
- 이름: {customer_info.get('name') or '고객'}
- 나이: {customer_info.get('age') or '알 수 없음'}세
- 현재 요금제: {customer_info.get('current_plan') or '없음 (타사 고객)'}
- 월 요금: {monthly_fee:,}원

## 대화 내용
{conversation_text}

## 다음 형식으로 JSON 응답해주세요:
{{
    "current_plan": "현재 사용 중인 요금제",
    "current_price": 현재 월 요금 (숫자만),
    "requested_feature": "고객이 원하는 기능/서비스 (예: 더 많은 데이터)",
    "customer_profile": "고객 특성 요약 (예: 가족 3명 KT 이용 중)",
    "main_concern": "고객의 주요 불만/관심사",
    "opportunity": "영업 기회 포인트 (예: 가족 결합 할인 가능)",
    "consultation_result": "상담 결과 - 고객이 최종 선택한 요금제/서비스 조합 (예: 5G 슬림 + 넷플릭스 스탠다드로 변경 희망)"
}}
"""

        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return ConversationSummary(
            current_plan=result.get("current_plan", customer_info.get("current_plan", "알 수 없음")),
            current_price=result.get("current_price", customer_info.get("monthly_fee", 0)),
            requested_feature=result.get("requested_feature", "특별한 요청 없음"),
            customer_profile=result.get("customer_profile", "정보 부족"),
            main_concern=result.get("main_concern", "특별한 불만 없음"),
            opportunity=result.get("opportunity", "추가 확인 필요"),
            consultation_result=result.get("consultation_result", "상담 진행 중")
        )

    def _format_conversation(self, conversation: List[Dict[str, Any]]) -> str:
        """대화 내용을 문자열로 포맷팅"""
        lines = []
        for msg in conversation:
            speaker = "AI 상담사" if msg.get("speaker") == "ai" else "고객"
            lines.append(f"{speaker}: {msg.get('content', '')}")
        return "\n".join(lines)


# 싱글톤 인스턴스
summary_service = SummaryService()
