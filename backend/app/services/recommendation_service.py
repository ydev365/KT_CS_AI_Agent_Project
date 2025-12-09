from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel

from ..core.config import settings
from ..utils.csv_loader import load_addon_services_csv, load_plans_csv
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
        self.addon_services = self._load_addon_services()
        self.all_plans = self._load_all_plans()

    def _load_all_plans(self) -> List[Dict[str, Any]]:
        """plans.csv에서 전체 요금제 정보 로드"""
        try:
            plans = load_plans_csv(settings.PLANS_CSV_PATH)
            print(f"[PLANS] Loaded {len(plans)} plans from CSV")
            return plans
        except Exception as e:
            print(f"[PLANS] Failed to load plans: {e}")
            return []

    def _load_addon_services(self) -> Dict[str, Dict[str, Any]]:
        """addon_services.csv에서 OTT 부가서비스 정보 로드"""
        try:
            services = load_addon_services_csv(settings.ADDON_SERVICES_CSV_PATH)
            # OTT 타입별로 가장 저렴한 서비스 찾기
            ott_services = {}
            for service in services:
                ott_type = service.get('ott_type')
                if ott_type and service.get('price', 0) > 0:
                    # 해당 OTT 타입이 없거나, 더 저렴하면 업데이트
                    if ott_type not in ott_services or service['price'] < ott_services[ott_type]['price']:
                        ott_services[ott_type] = service
            print(f"[ADDON] Loaded {len(ott_services)} OTT services from CSV")
            return ott_services
        except Exception as e:
            print(f"[ADDON] Failed to load addon services: {e}")
            return {}

    def get_addon_price(self, ott_name: str) -> tuple[str, int]:
        """OTT 이름으로 부가서비스 이름과 가격 조회"""
        ott_name_lower = ott_name.lower()

        # OTT 키워드 매핑
        ott_mapping = {
            '넷플릭스': '넷플릭스',
            'netflix': '넷플릭스',
            '티빙': '티빙',
            'tving': '티빙',
            '디즈니': '디즈니+',
            'disney': '디즈니+',
            '유튜브': '유튜브프리미엄',
            'youtube': '유튜브프리미엄',
        }

        # 매핑된 OTT 타입 찾기
        ott_type = None
        for keyword, mapped_type in ott_mapping.items():
            if keyword in ott_name_lower:
                ott_type = mapped_type
                break

        if ott_type and ott_type in self.addon_services:
            service = self.addon_services[ott_type]
            return service['service_name'], service['price']

        return None, 0

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
                conversation_history=conversation_history,
                target_categories=target_categories
            )

        # 대화 기록 없으면 기존 GPT 기반 추천
        return await self._generate_gpt_based_recommendations(
            plans=plans,
            context=context,
            summary=summary
        )

    def _detect_plan_category_from_conversation(self, conversation_history: List[Dict[str, Any]]) -> str:
        """대화에서 요금제 카테고리 감지 (Y요금제, 시니어 등)"""
        if not conversation_history:
            return None

        conversation_text = ' '.join([
            msg.get('content', '') for msg in conversation_history
        ]).lower()

        # Y요금제 (청년)
        y_keywords = ['청년', 'y요금제', 'y 요금제', '5g y', 'y베이직', 'y슬림', 'y 베이직', 'y 슬림']
        if any(kw in conversation_text for kw in y_keywords):
            return 'Y'

        # 시니어
        senior_keywords = ['시니어', '어르신', '65세']
        if any(kw in conversation_text for kw in senior_keywords):
            return '시니어'

        # Y틴
        teen_keywords = ['y틴', 'yteen', '청소년', '학생 요금']
        if any(kw in conversation_text for kw in teen_keywords):
            return 'Y틴'

        # 주니어
        junior_keywords = ['주니어', '어린이', '키즈']
        if any(kw in conversation_text for kw in junior_keywords):
            return '주니어'

        return None

    def _filter_plans_by_category(self, plans: List[Dict], category: str) -> List[Dict]:
        """카테고리에 맞는 요금제만 필터링"""
        if not category:
            return plans

        category_keywords = {
            'Y': ['5g y', ' y ', 'y 베이직', 'y 슬림', 'y 세이브', 'y 초이스', 'y베이직', 'y슬림', 'y세이브', 'y초이스'],
            '시니어': ['시니어'],
            'Y틴': ['y틴', 'yteen'],
            '주니어': ['주니어', 'junior']
        }

        keywords = category_keywords.get(category, [])
        if not keywords:
            return plans

        filtered = [
            p for p in plans
            if any(kw in p.get('plan_name', '').lower() for kw in keywords)
        ]

        print(f"[RECOMMEND] Filtered to {len(filtered)} {category} plans from {len(plans)} total")
        return filtered if filtered else plans

    async def _generate_scoring_based_recommendations(
        self,
        plans: List[Dict],
        context: str,
        summary: ConversationSummary,
        conversation_history: List[Dict[str, Any]],
        target_categories: List[str] = None
    ) -> List[PlanRecommendation]:
        """스코어링 기반 추천 생성"""
        # 대화에서 요금제 카테고리 감지 (Y요금제, 시니어 등)
        plan_category = self._detect_plan_category_from_conversation(conversation_history)
        if plan_category:
            print(f"[RECOMMEND] Detected plan category from conversation: {plan_category}")
            # 해당 카테고리 요금제만 필터링
            plans = self._filter_plans_by_category(plans, plan_category)
            # all_plans에서도 필터링 (budget용)
            self._filtered_all_plans = self._filter_plans_by_category(self.all_plans, plan_category)
        else:
            self._filtered_all_plans = self.all_plans

        # 대화 내용 분석하여 고객 니즈 파악
        needs = scoring_service.analyze_customer_needs(conversation_history)
        # 고객 타겟 카테고리 설정 (Y요금제, 시니어 등 매칭용)
        needs.target_categories = target_categories or []

        # 스코어링 기반으로 2가지 유형 선정 (최적형, 업그레이드형)
        best_plan, upsell_plan, _ = scoring_service.select_recommendations(
            plans=plans,
            needs=needs
        )

        recommendations = []

        # 1. 최적형
        if best_plan:
            score = scoring_service.calculate_plan_score(best_plan, needs, plans)
            breakdown = scoring_service.get_score_breakdown(best_plan, needs, plans)
            comparison = await self._generate_comparison_text(
                plan=best_plan, badge="best", type_name="최적형",
                summary=summary, score=score
            )
            recommendations.append(PlanRecommendation(
                id=1,
                name=best_plan.get("plan_name", "알 수 없음"),
                price=best_plan.get("price", 0),
                discounted_price=best_plan.get("price", 0),
                discount="할인 없음",
                data=str(best_plan.get("data_gb", "정보 없음")),
                features=self._extract_features(best_plan),
                badge="best",
                comparison=comparison,
                score=score,
                score_breakdown=breakdown
            ))

        # 2. 업그레이드형
        if upsell_plan:
            score = scoring_service.calculate_plan_score(upsell_plan, needs, plans)
            breakdown = scoring_service.get_score_breakdown(upsell_plan, needs, plans)
            comparison = await self._generate_comparison_text(
                plan=upsell_plan, badge="upsell", type_name="업그레이드형",
                summary=summary, score=score
            )
            recommendations.append(PlanRecommendation(
                id=2,
                name=upsell_plan.get("plan_name", "알 수 없음"),
                price=upsell_plan.get("price", 0),
                discounted_price=upsell_plan.get("price", 0),
                discount="할인 없음",
                data=str(upsell_plan.get("data_gb", "정보 없음")),
                features=self._extract_features(upsell_plan),
                badge="upsell",
                comparison=comparison,
                score=score,
                score_breakdown=breakdown
            ))

        # 3. 절약형: best보다 저렴한 요금제
        best_price = best_plan.get('price', 0) if best_plan else 999999
        budget_combo = self._create_budget_combo(plans, needs, summary, target_categories, best_price)
        if budget_combo:
            recommendations.append(budget_combo)

        return recommendations

    def _create_budget_combo(
        self,
        plans: List[Dict],
        needs,
        summary: ConversationSummary,
        target_categories: List[str] = None,
        best_price: int = 999999
    ) -> PlanRecommendation:
        """절약형: best보다 저렴한 요금제 추천"""
        # Budget은 전체 요금제에서 검색 (대화 맥락 카테고리에 국한하지 않음)
        # → Best/Upsell은 Y요금제만, Budget은 더 싼 거면 일반 요금제도 OK
        all_plans = self.all_plans if self.all_plans else plans

        # best보다 저렴한 요금제만 필터링
        cheaper_plans = [p for p in all_plans if p.get('price', 999999) < best_price]

        if not cheaper_plans:
            print(f"[BUDGET] No plans cheaper than best ({best_price}원), skipping")
            return None

        budget_plans = []

        # 타겟별 저렴한 요금제 키워드
        budget_keywords = ['슬림']  # 기본

        if target_categories:
            # 특수 타겟 확인
            target_str = ' '.join(target_categories)
            if '34세' in target_str or 'Y' in target_str or '청년' in target_str:
                budget_keywords = ['Y 슬림', 'Y슬림', 'Y세이브']
            elif '65세' in target_str or '시니어' in target_str:
                budget_keywords = ['시니어']
            elif '12세' in target_str or '주니어' in target_str:
                budget_keywords = ['주니어 슬림', '주니어']
            elif '외국인' in target_str:
                budget_keywords = ['웰컴']
            elif '장애인' in target_str or '복지' in target_str:
                budget_keywords = ['복지']

        print(f"[BUDGET] Searching in {len(cheaper_plans)} cheaper plans (< {best_price}원) with keywords: {budget_keywords}")

        # 1. best보다 저렴한 요금제 중 타겟에 맞는 것 찾기
        for plan in cheaper_plans:
            plan_name = plan.get('plan_name', '')
            plan_target = plan.get('target', '전체')

            # 저렴한 키워드 매칭
            if any(kw in plan_name for kw in budget_keywords):
                # 타겟도 맞는지 확인
                if target_categories:
                    if any(cat in plan_target for cat in target_categories) or plan_target == '전체':
                        budget_plans.append(plan)
                else:
                    budget_plans.append(plan)

        # 2. 타겟 맞는 요금제 없으면 cheaper_plans에서 슬림 계열 찾기 (타겟도 체크!)
        if not budget_plans:
            for plan in cheaper_plans:
                plan_name = plan.get('plan_name', '')
                plan_target = plan.get('target', '전체')

                if '슬림' in plan_name:
                    # 타겟 체크: 고객 타겟에 맞거나 '전체'인 경우만
                    is_target_match = False
                    if plan_target == '전체':
                        is_target_match = True
                    elif target_categories:
                        # 고객 타겟과 요금제 타겟이 맞는지 확인
                        for cat in target_categories:
                            if cat in plan_target or plan_target in cat:
                                is_target_match = True
                                break
                        # 주니어/시니어 등 다른 연령대 요금제 제외
                        if '주니어' in plan_name and '12세' not in ' '.join(target_categories):
                            is_target_match = False
                        if '시니어' in plan_name and '65세' not in ' '.join(target_categories):
                            is_target_match = False
                        if 'Y틴' in plan_name and '18세' not in ' '.join(target_categories):
                            is_target_match = False

                    if is_target_match:
                        budget_plans.append(plan)

            print(f"[BUDGET] No target-specific plans, found {len(budget_plans)} slim plans matching target")

        # 3. 슬림도 없으면 cheaper_plans에서 타겟 맞는 가장 저렴한 것
        if not budget_plans:
            # 타겟 필터링: 주니어/시니어/Y틴 등 다른 연령대 제외
            target_str = ' '.join(target_categories) if target_categories else ''
            filtered_cheaper = []
            for plan in cheaper_plans:
                plan_name = plan.get('plan_name', '')
                # 다른 연령대 요금제 제외
                if '주니어' in plan_name and '12세' not in target_str:
                    continue
                if '시니어' in plan_name and '65세' not in target_str:
                    continue
                if 'Y틴' in plan_name and '18세' not in target_str:
                    continue
                filtered_cheaper.append(plan)

            budget_plans = sorted(filtered_cheaper, key=lambda x: x.get('price', 999999))[:3]
            print(f"[BUDGET] No slim plans, using cheapest from {len(filtered_cheaper)} target-compatible plans")

        if not budget_plans:
            print("[BUDGET] No budget plans found, skipping")
            return None

        # 가장 저렴한 요금제 선택
        budget_plans = sorted(budget_plans, key=lambda x: x.get('price', 999999))
        base_plan = budget_plans[0]
        base_price = base_plan.get('price', 0)
        base_name = base_plan.get('plan_name', '알 수 없음')

        print(f"[BUDGET] Selected: {base_name} ({base_price}원) | target: {base_plan.get('target')} | categories: {target_categories}")

        # 스코어 계산 (전체 요금제 기준)
        score = scoring_service.calculate_plan_score(base_plan, needs, all_plans)

        # 고객이 OTT를 원하면 → 슬림 + OTT 조합
        if needs.desired_otts:
            ott = needs.desired_otts[0]
            # CSV에서 OTT 부가서비스 정보 가져오기
            addon_name, addon_price = self.get_addon_price(ott)

            if addon_name and addon_price > 0:
                total_price = base_price + addon_price
                return PlanRecommendation(
                    id=3,
                    name=f"{base_name} + {addon_name}",
                    price=total_price,
                    discounted_price=total_price,
                    discount="조합 할인",
                    data=str(base_plan.get("data_gb", "정보 없음")),
                    features=[
                        f"요금제: {base_name} ({base_price:,}원)",
                        f"부가서비스: {addon_name} ({addon_price:,}원)",
                        f"합계: {total_price:,}원/월"
                    ],
                    badge="budget",
                    comparison=f"저렴한 {base_name}에 {addon_name}을 추가하면 월 {total_price:,}원에 이용 가능합니다.",
                    score=score,
                    score_breakdown=None
                )

        # OTT 안 원하면 → 슬림 요금제만 추천
        return PlanRecommendation(
            id=3,
            name=base_name,
            price=base_price,
            discounted_price=base_price,
            discount="할인 없음",
            data=str(base_plan.get("data_gb", "정보 없음")),
            features=self._extract_features(base_plan),
            badge="budget",
            comparison=f"기본에 충실한 {base_name}으로 월 {base_price:,}원에 이용 가능합니다.",
            score=score,
            score_breakdown=None
        )

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
