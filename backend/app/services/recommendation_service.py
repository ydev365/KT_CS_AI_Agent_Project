from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel

from ..core.config import settings
from .rag_service import rag_service
from .summary_service import ConversationSummary
from .scoring_service import scoring_service, CustomerNeeds


class PlanRecommendation(BaseModel):
    """요금제 추천"""
    id: int
    name: str
    price: int
    discounted_price: int
    discount: str
    data: str
    features: List[str]
    badge: str  # "best", "upsell", "budget"
    comparison: str
    score: Optional[float] = None  # 스코어링 점수
    score_breakdown: Optional[Dict[str, Any]] = None  # 점수 상세 내역


class RecommendationResult(BaseModel):
    """추천 결과"""
    summary: ConversationSummary
    recommended_plans: List[PlanRecommendation]


class RecommendationService:
    """요금제 추천 서비스"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_recommendations(
        self,
        summary: ConversationSummary,
        customer_info: Dict[str, Any],
        target_categories: List[str],
        conversation_history: List[Dict[str, Any]] = None
    ) -> List[PlanRecommendation]:
        """
        스코어링 기반 3가지 유형의 요금제 추천 생성

        Args:
            summary: 대화 요약
            customer_info: 고객 정보
            target_categories: 고객 타겟 카테고리
            conversation_history: 대화 기록 (스코어링용)

        Returns:
            추천 요금제 리스트 (best, upsell, budget)
        """
        # 요약 기반 검색 쿼리 생성
        search_query = f"{summary.requested_feature} {summary.main_concern}"

        # RAG로 관련 요금제 검색
        plans, context = rag_service.get_relevant_plans_with_context(
            query=search_query,
            target_categories=target_categories,
            top_k=10
        )

        if not plans:
            return []

        # 대화 기록이 있으면 스코어링 기반 추천
        if conversation_history:
            return await self._generate_scoring_based_recommendations(
                plans=plans,
                context=context,
                summary=summary,
                conversation_history=conversation_history
            )

        # 대화 기록 없으면 기존 GPT 기반 추천
        return await self._generate_gpt_based_recommendations(
            plans=plans,
            context=context,
            summary=summary
        )

    async def _generate_scoring_based_recommendations(
        self,
        plans: List[Dict],
        context: str,
        summary: ConversationSummary,
        conversation_history: List[Dict[str, Any]]
    ) -> List[PlanRecommendation]:
        """스코어링 기반 추천 생성"""
        # 대화 내용 분석하여 고객 니즈 파악
        needs = scoring_service.analyze_customer_needs(conversation_history)

        # 스코어링 기반으로 3가지 유형 선정
        best_plan, upsell_plan, budget_plan = scoring_service.select_recommendations(
            plans=plans,
            needs=needs
        )

        # GPT로 비교 설명 생성
        recommendations = []
        plan_types = [
            (best_plan, "best", "최적형"),
            (upsell_plan, "upsell", "업그레이드형"),
            (budget_plan, "budget", "절약형")
        ]

        for plan, badge, type_name in plan_types:
            if plan:
                score = scoring_service.calculate_plan_score(plan, needs, plans)
                breakdown = scoring_service.get_score_breakdown(plan, needs, plans)

                comparison = await self._generate_comparison_text(
                    plan=plan,
                    badge=badge,
                    type_name=type_name,
                    summary=summary,
                    score=score
                )

                recommendations.append(PlanRecommendation(
                    id=len(recommendations) + 1,
                    name=plan.get("plan_name", "알 수 없음"),
                    price=plan.get("price", 0),
                    discounted_price=plan.get("discounted_price", plan.get("price", 0)),
                    discount=plan.get("discount", "할인 없음"),
                    data=str(plan.get("data_gb", "정보 없음")),
                    features=self._extract_features(plan),
                    badge=badge,
                    comparison=comparison,
                    score=score,
                    score_breakdown=breakdown
                ))

        return recommendations

    def _extract_features(self, plan: Dict) -> List[str]:
        """요금제에서 주요 기능 추출"""
        features = []

        # 데이터
        data = plan.get("data_gb")
        if data:
            features.append(f"데이터 {data}")

        # OTT
        choice = plan.get("choice")
        if choice and choice != "없음":
            features.append(f"OTT: {choice}")

        # 로밍
        roaming = plan.get("data_roam")
        if roaming and roaming != "None":
            features.append(f"해외로밍 {roaming}")

        # 멤버십
        membership = plan.get("membership")
        if membership:
            features.append(f"멤버십 {membership}")

        return features[:4]  # 최대 4개

    async def _generate_comparison_text(
        self,
        plan: Dict,
        badge: str,
        type_name: str,
        summary: ConversationSummary,
        score: float
    ) -> str:
        """GPT로 비교 멘트 생성"""
        prompt = f"""상담사가 고객에게 설명할 한 줄 멘트를 생성해주세요.

요금제: {plan.get('plan_name')}
유형: {type_name} ({badge})
가격: {plan.get('price', 0):,}원
고객 현재 요금: {summary.current_price:,}원
고객 요구사항: {summary.requested_feature}
AI 스코어: {score:.1f}점

한 문장으로 핵심만 설명하세요 (예: "현재보다 월 2만원 저렴하면서 데이터는 무제한입니다")
"""
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception:
            price_diff = plan.get('price', 0) - summary.current_price
            if price_diff > 0:
                return f"월 {price_diff:,}원 추가로 더 좋은 혜택을 받으실 수 있습니다."
            elif price_diff < 0:
                return f"월 {abs(price_diff):,}원 절약하실 수 있습니다."
            return "고객님 조건에 맞는 요금제입니다."

    async def _generate_gpt_based_recommendations(
        self,
        plans: List[Dict],
        context: str,
        summary: ConversationSummary
    ) -> List[PlanRecommendation]:
        """GPT 기반 추천 (fallback)"""
        prompt = f"""AI 상담이 끝났습니다. 이제 실제 상담사가 고객과 통화합니다.
상담사가 참고할 수 있도록 3가지 유형의 요금제를 추천해주세요.

## AI 상담 요약
- 현재 요금제: {summary.current_plan}
- 현재 월 요금: {summary.current_price:,}원
- 고객이 원하는 것: {summary.requested_feature}
- 주요 관심사: {summary.main_concern}
- 고객 특성: {summary.customer_profile}
- 영업 기회: {summary.opportunity}

## 검색된 요금제 정보
{context}

## 3가지 유형으로 추천 (상담사가 상황에 맞게 선택)
1. **best (최적형)**: 고객 요구에 가장 부합 - 상담사가 우선 제안할 요금제
2. **upsell (업그레이드형)**: 더 좋은 혜택 - 고객이 관심 보이면 업셀링 가능
3. **budget (절약형)**: 비용 절감 - 가격에 민감한 고객에게 대안

## JSON 형식 (정확히 3개):
{{
    "recommendations": [
        {{
            "id": 1,
            "name": "요금제명",
            "price": 원가(숫자),
            "discounted_price": 할인가(숫자),
            "discount": "할인 정보",
            "data": "데이터량",
            "features": ["주요 기능1", "주요 기능2", "주요 기능3"],
            "badge": "best/upsell/budget",
            "comparison": "현재 대비 비교 설명 (상담사가 고객에게 말할 멘트)"
        }}
    ]
}}

중요: 검색된 요금제 중에서만 선택하고, 가격은 정확히!
"""

        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        recommendations = []
        for rec in result.get("recommendations", [])[:3]:
            recommendations.append(PlanRecommendation(
                id=rec.get("id", len(recommendations) + 1),
                name=rec.get("name", "알 수 없음"),
                price=rec.get("price", 0),
                discounted_price=rec.get("discounted_price", rec.get("price", 0)),
                discount=rec.get("discount", "할인 없음"),
                data=rec.get("data", "정보 없음"),
                features=rec.get("features", []),
                badge=rec.get("badge", "best"),
                comparison=rec.get("comparison", "")
            ))

        return recommendations


# 싱글톤 인스턴스
recommendation_service = RecommendationService()
