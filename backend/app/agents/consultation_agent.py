from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI

from ..core.config import settings
from ..schemas.auth import AuthResult
from ..services.rag_service import rag_service
from .prompts.system_prompts import (
    CONSULTATION_SYSTEM_PROMPT,
    GREETING_TEMPLATE,
    PERSONALIZED_GREETINGS,
    SESSION_END_DETECTION_PROMPT
)


@dataclass
class AgentResponse:
    """에이전트 응답"""
    text: str
    should_end: bool = False
    plans_mentioned: Optional[List[str]] = None


class ConsultationAgent:
    """AI 상담 에이전트"""

    def __init__(self, customer_info: AuthResult):
        self.customer_info = customer_info
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """고객 맞춤 시스템 프롬프트 생성"""
        return CONSULTATION_SYSTEM_PROMPT.format(
            customer_name=self.customer_info.name or "고객",
            age=self.customer_info.age,
            current_plan=self.customer_info.current_plan or "없음 (타사 고객)",
            monthly_fee=f"{self.customer_info.monthly_fee:,}원" if self.customer_info.monthly_fee else "없음",
            target_categories=", ".join(self.customer_info.target_categories)
        )

    def generate_greeting(self) -> str:
        """첫 인사말 생성"""
        customer_name = self.customer_info.name or "고객"
        primary_target = self.customer_info.primary_target

        # 맞춤 인사말
        personalized_message = PERSONALIZED_GREETINGS.get(
            primary_target,
            PERSONALIZED_GREETINGS["전체"]
        )

        greeting = GREETING_TEMPLATE.format(
            customer_name=customer_name,
            personalized_message=personalized_message
        )

        # 대화 기록에 추가
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })

        return greeting

    def _check_should_end(self, message: str) -> bool:
        """상담 종료 여부 판단"""
        end_keywords = [
            # 상담사 연결 요청
            "상담사 연결", "상담원 연결", "사람과 통화", "직원 연결",
            "상담사랑", "상담원이랑", "사람이랑", "사람한테",
            "상담사로", "상담원으로", "전문 상담", "실제 상담",
            "연결해줘", "연결해주세요", "연결 해줘", "연결 해주세요",
            # 상담 종료 요청
            "상담 끝", "상담 종료", "그만할게요", "그만 할게요",
            "끝낼게요", "끝낼게", "종료해줘", "종료 해줘"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in end_keywords)

    def _search_relevant_plans(self, message: str) -> tuple[List[Dict], str]:
        """메시지에서 관련 요금제 검색"""
        # 요금제 관련 키워드 확인
        plan_keywords = [
            "요금제", "데이터", "무제한", "가격", "얼마", "추천",
            "비교", "변경", "저렴", "싼", "혜택", "할인",
            "차이", "다른", "뭐가 달라", "어떻게 달라", "차이점",
            "OTT", "넷플릭스", "티빙", "디즈니", "유튜브", "밀리"
        ]

        # 이전 대화에서 언급된 요금제 찾기
        mentioned_plans = []
        for hist in self.conversation_history:
            content = hist.get("content", "")
            # 대화에서 요금제명 추출 (5G, LTE로 시작하는 요금제)
            if "5G" in content or "LTE" in content:
                mentioned_plans.append(content)

        # 현재 메시지에 키워드가 있거나, 이전에 요금제가 언급되었으면 검색
        should_search = any(kw in message for kw in plan_keywords)

        # "차이", "비교" 등 비교 질문이면 이전 대화 맥락 포함해서 검색
        is_comparison_question = any(kw in message for kw in ["차이", "비교", "다른", "달라"])

        if should_search or is_comparison_question:
            # 비교 질문이면 이전 대화 맥락을 쿼리에 포함
            if is_comparison_question and mentioned_plans:
                # 최근 AI 응답에서 언급된 요금제명 추출해서 검색
                recent_context = " ".join([h["content"] for h in self.conversation_history[-4:]])
                search_query = f"{recent_context} {message}"
            else:
                search_query = message

            return rag_service.get_relevant_plans_with_context(
                query=search_query,
                target_categories=self.customer_info.target_categories,
                top_k=5
            )

        return [], ""

    def _extract_known_info(self) -> str:
        """대화에서 이미 파악된 고객 정보 추출"""
        known_info = []

        # 고객 발화만 추출
        customer_messages = " ".join([
            msg["content"] for msg in self.conversation_history
            if msg["role"] == "user"
        ]).lower()

        # OTT 관련
        ott_keywords = {
            "넷플릭스": ["넷플릭스", "netflix", "넷플"],
            "티빙": ["티빙", "tving"],
            "디즈니+": ["디즈니", "disney"],
            "유튜브": ["유튜브", "youtube"],
            "웨이브": ["웨이브", "wavve"]
        }
        wanted_otts = []
        for ott, keywords in ott_keywords.items():
            if any(kw in customer_messages for kw in keywords):
                wanted_otts.append(ott)
        if wanted_otts:
            known_info.append(f"- 원하는 OTT: {', '.join(wanted_otts)}")

        # 가격 관련
        if any(kw in customer_messages for kw in ["저렴", "싼", "싸게", "저럼", "절약", "아끼"]):
            known_info.append("- 예산: 저렴한 요금제 선호")
        elif any(kw in customer_messages for kw in ["비싸도", "상관없"]):
            known_info.append("- 예산: 가격보다 혜택 중시")

        # 데이터 관련
        if any(kw in customer_messages for kw in ["데이터 많이", "무제한", "데이터 자주"]):
            known_info.append("- 데이터: 많이 사용")
        elif any(kw in customer_messages for kw in ["데이터 적게", "데이터 안", "많이 안"]):
            known_info.append("- 데이터: 적게 사용")

        # 해외/로밍 관련
        if any(kw in customer_messages for kw in ["해외", "로밍", "여행", "출장"]):
            known_info.append("- 해외로밍: 필요")

        if known_info:
            return "\n\n## 이미 파악된 고객 조건 (다시 묻지 마세요!)\n" + "\n".join(known_info)
        return ""

    async def process_message(self, user_message: str) -> AgentResponse:
        """
        고객 메시지 처리 및 응답 생성

        Args:
            user_message: 고객 메시지

        Returns:
            에이전트 응답
        """
        # 종료 여부 확인
        should_end = self._check_should_end(user_message)

        if should_end:
            end_response = "네, 지금 바로 전문 상담사에게 연결해드리겠습니다. 지금까지 상담 내용을 전달해드릴게요. 잠시만 기다려주세요."
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": end_response})
            return AgentResponse(text=end_response, should_end=True)

        # 대화 기록에 사용자 메시지 추가
        self.conversation_history.append({"role": "user", "content": user_message})

        # RAG 검색
        plans, rag_context = self._search_relevant_plans(user_message)

        # 이미 파악된 정보 추출
        known_info = self._extract_known_info()

        # 메시지 구성
        messages = [{"role": "system", "content": self.system_prompt + known_info}]

        # RAG 컨텍스트가 있으면 추가
        if rag_context:
            messages.append({
                "role": "system",
                "content": f"\n\n{rag_context}"
            })

        # 대화 기록 추가
        messages.extend(self.conversation_history)

        # GPT 호출 (전화 상담이므로 20초 분량, 약 2문장)
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=150  # 약간 늘림 - 자연스러운 대화를 위해
        )

        assistant_message = response.choices[0].message.content

        # 대화 기록에 추가
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        # 언급된 요금제 추출
        plans_mentioned = [p["plan_name"] for p in plans] if plans else None

        return AgentResponse(
            text=assistant_message,
            should_end=False,
            plans_mentioned=plans_mentioned
        )

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """대화 기록 반환"""
        return self.conversation_history

    def get_conversation_for_summary(self) -> str:
        """요약을 위한 대화 내용 문자열"""
        lines = []
        for msg in self.conversation_history:
            role = "AI 상담사" if msg["role"] == "assistant" else "고객"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
