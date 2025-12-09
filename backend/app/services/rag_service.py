from typing import List, Dict, Any, Optional, Tuple
from .vector_db_service import vector_db_service


class RAGService:
    """RAG (Retrieval-Augmented Generation) 서비스"""

    def __init__(self):
        self.vector_db = vector_db_service

    def _analyze_query_intent(self, query: str) -> Tuple[Optional[Dict], Optional[str], str, Optional[str]]:
        """
        쿼리에서 필터링/정렬 의도 분석

        Returns:
            (filters, sort_by, sort_order, plan_category)
        """
        query_lower = query.lower()
        filters = {}
        sort_by = None
        sort_order = "asc"
        plan_category = None  # Y요금제, 시니어 등 맥락 카테고리

        # 맥락에서 요금제 카테고리 감지
        y_plan_keywords = ["청년", "y 요금제", "y요금제", "5g y", "y 베이직", "y 슬림", "y세이브", "y베이직", "y슬림"]
        senior_keywords = ["시니어", "어르신", "65세"]
        teen_keywords = ["y틴", "yteen", "청소년", "학생"]
        junior_keywords = ["주니어", "어린이", "키즈"]

        if any(kw in query_lower for kw in y_plan_keywords):
            plan_category = "Y"
            print(f"[RAG] Detected Y요금제 context")
        elif any(kw in query_lower for kw in senior_keywords):
            plan_category = "시니어"
        elif any(kw in query_lower for kw in teen_keywords):
            plan_category = "Y틴"
        elif any(kw in query_lower for kw in junior_keywords):
            plan_category = "주니어"

        # OTT 관련 키워드 감지
        ott_keywords = ["ott", "넷플릭스", "티빙", "디즈니", "유튜브", "netflix", "tving", "disney"]
        if any(kw in query_lower for kw in ott_keywords):
            filters["has_ott"] = True

        # 가격 관련 키워드 감지
        cheap_keywords = ["싼", "저렴", "싸", "최저", "제일 싼", "가장 싼", "저럼", "싼거", "싼 거"]
        expensive_keywords = ["비싼", "프리미엄", "고급", "최고"]

        if any(kw in query_lower for kw in cheap_keywords):
            sort_by = "price"
            sort_order = "asc"
        elif any(kw in query_lower for kw in expensive_keywords):
            sort_by = "price"
            sort_order = "desc"

        # 무제한 데이터 키워드 감지
        if "무제한" in query_lower:
            filters["has_unlimited_data"] = True

        return (filters if filters else None, sort_by, sort_order, plan_category)

    def search_plans(
        self,
        query: str,
        target_categories: Optional[List[str]] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[Dict[str, Any]]:
        """
        고객 질문에 맞는 요금제 검색

        Args:
            query: 검색 쿼리
            target_categories: 고객이 해당하는 타겟 카테고리 리스트
            top_k: 반환할 결과 수
            filters: 필터 조건
            sort_by: 정렬 기준
            sort_order: 정렬 순서

        Returns:
            검색된 요금제 리스트
        """
        return self.vector_db.search(
            query=query,
            target_categories=target_categories,
            top_k=top_k,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )

    def build_context(
        self,
        plans: List[Dict[str, Any]],
        combo_options: Optional[List[Dict]] = None,
        is_ott_related: bool = False
    ) -> str:
        """
        검색된 요금제로 LLM 컨텍스트 생성

        Args:
            plans: 검색된 요금제 리스트
            combo_options: 요금제+부가서비스 조합 옵션 리스트
            is_ott_related: OTT 관련 질문 여부

        Returns:
            LLM에 제공할 컨텍스트 문자열
        """
        if not plans and not combo_options:
            return "검색된 요금제가 없습니다."

        context_parts = []

        # OTT 관련 질문이면 조합 옵션 정보 항상 포함
        if is_ott_related and combo_options:
            context_parts.append("[OTT 이용 방법 안내]")
            context_parts.append("")
            context_parts.append("방법 1) OTT 포함 요금제")
            # OTT 포함 요금제 중 최저가 찾기
            ott_plans = [p for p in plans if p.get("has_ott")]
            if ott_plans:
                cheapest_ott = min(ott_plans, key=lambda x: x.get("price", 0))
                context_parts.append(f"  - 최저가: {cheapest_ott['plan_name']} ({cheapest_ott['price']:,}원)")
            context_parts.append("")
            context_parts.append("방법 2) 기본 요금제 + OTT 부가서비스 조합 (더 저렴할 수 있음)")
            for i, combo in enumerate(combo_options[:3], 1):
                context_parts.append(f"  조합{i}: {combo['plan_name']}({combo['plan_price']:,}원) + {combo['addon_name']}({combo['addon_price']:,}원) = {combo['total_price']:,}원")
                if combo.get('savings', 0) > 0:
                    context_parts.append(f"         → {combo['savings']:,}원 절약 가능")
            context_parts.append("")
            context_parts.append("※ 고객이 가격에 민감하면 조합을 추천하세요")
            context_parts.append("※ 조합 추천 시 먼저 원하는 OTT를 확인하세요")
            context_parts.append("=" * 50)
            context_parts.append("")

        context_parts.append("[검색된 요금제 정보]")

        for i, plan in enumerate(plans, 1):
            context_parts.append(f"\n{'='*40}")
            context_parts.append(f"【요금제 {i}】")
            context_parts.append(f"{'='*40}")
            context_parts.append(plan["document"])

        return "\n".join(context_parts)

    def _get_combo_options(
        self,
        target_categories: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        기본 요금제 + OTT 부가서비스 조합 옵션들 생성

        Returns:
            조합 옵션 리스트 (가격순 정렬)
        """
        # OTT 포함 요금제 최저가 조회 (비교 기준)
        ott_plans = self.vector_db.search(
            query="OTT 요금제",
            target_categories=target_categories,
            filters={"has_ott": True},
            sort_by="price",
            sort_order="asc",
            top_k=1
        )

        ott_plan_price = ott_plans[0]["price"] if ott_plans else 90000  # 기본값

        # OTT 미포함 저렴한 요금제 조회
        basic_plans = self.vector_db.search(
            query="기본 요금제",
            target_categories=target_categories,
            filters={"has_ott": False},
            sort_by="price",
            sort_order="asc",
            top_k=5
        )

        if not basic_plans:
            return []

        # OTT 부가서비스 조회 (OTT별 최저가)
        all_addons = self.vector_db.get_cheapest_addon_by_ott()

        if not all_addons:
            return []

        # OTT 종류별 최저가만 추출
        ott_type_cheapest = {}
        for addon in all_addons:
            ott_type = addon.get("ott_type")
            if ott_type and ott_type not in ott_type_cheapest:
                ott_type_cheapest[ott_type] = addon

        # 모든 조합 생성
        combos = []
        for plan in basic_plans:
            plan_price = plan["price"]

            for ott_type, addon in ott_type_cheapest.items():
                addon_price = addon["price"]
                total = plan_price + addon_price
                savings = ott_plan_price - total

                combos.append({
                    "plan_name": plan["plan_name"],
                    "plan_price": plan_price,
                    "addon_name": addon["service_name"],
                    "addon_price": addon_price,
                    "addon_ott_type": ott_type,
                    "total_price": total,
                    "ott_plan_price": ott_plan_price,
                    "savings": savings
                })

        # 가격순 정렬 후 상위 N개 반환
        combos.sort(key=lambda x: x["total_price"])
        return combos[:top_k]

    def _is_ott_related(self, query: str) -> bool:
        """OTT 관련 질문인지 판단 (벡터 유사도 기반으로 확장 가능)"""
        query_lower = query.lower()
        # 기본 키워드 체크 (최소한의 하드코딩)
        ott_indicators = ["ott", "넷플릭스", "티빙", "디즈니", "유튜브", "영상", "스트리밍", "netflix", "tving"]
        return any(kw in query_lower for kw in ott_indicators)

    def get_relevant_plans_with_context(
        self,
        query: str,
        target_categories: Optional[List[str]] = None,
        top_k: int = 5
    ) -> tuple[List[Dict[str, Any]], str]:
        """
        요금제 검색 및 컨텍스트 생성 (자동 필터링/정렬 적용)

        Returns:
            (검색된 요금제 리스트, LLM 컨텍스트)
        """
        # 쿼리 의도 분석
        filters, sort_by, sort_order, plan_category = self._analyze_query_intent(query)

        # OTT 관련 질문인지 판단
        is_ott_related = self._is_ott_related(query)
        print(f"[RAG] OTT related: {is_ott_related}")

        # OTT 관련이면 조합 옵션 항상 준비 (GPT가 상황에 맞게 활용)
        combo_options = None
        if is_ott_related:
            combo_options = self._get_combo_options(target_categories, top_k=5)
            print(f"[RAG] Combo options count: {len(combo_options) if combo_options else 0}")

        # 카테고리가 감지되면 검색 쿼리에 카테고리 추가
        search_query = query
        if plan_category:
            category_search_terms = {
                "Y": "5G Y 청년 요금제",
                "시니어": "시니어 요금제",
                "Y틴": "Y틴 청소년 요금제",
                "주니어": "주니어 어린이 요금제"
            }
            search_query = f"{category_search_terms.get(plan_category, '')} {query}"
            print(f"[RAG] Enhanced search query for {plan_category}: {search_query[:50]}...")

        # 검색 수행 (필터 + 정렬 적용)
        plans = self.search_plans(
            query=search_query,
            target_categories=target_categories,
            top_k=top_k * 2 if plan_category else top_k,  # 카테고리 필터링 시 더 많이 검색
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # 맥락 카테고리가 있으면 해당 카테고리 요금제만 필터링
        category_hint = ""
        if plan_category and plans:
            category_keywords = {
                "Y": ["5g y", " y ", "y 베이직", "y 슬림", "y 세이브", "y 초이스", "y베이직", "y슬림", "y세이브", "y초이스"],
                "시니어": ["시니어", "senior"],
                "Y틴": ["y틴", "yteen", "y 틴"],
                "주니어": ["주니어", "junior", "키즈"]
            }
            keywords = category_keywords.get(plan_category, [])
            if keywords:
                # 디버깅: 검색된 요금제 이름 출력
                plan_names = [p.get("plan_name", "unknown") for p in plans]
                print(f"[RAG] Plans before filter: {plan_names[:5]}")

                filtered_plans = [
                    p for p in plans
                    if any(kw in p.get("plan_name", "").lower() for kw in keywords)
                ]
                if filtered_plans:
                    plans = filtered_plans[:top_k]
                    category_hint = f"[{plan_category} 요금제만 필터링됨]\n\n"
                    print(f"[RAG] Filtered to {len(plans)} {plan_category} plans: {[p.get('plan_name') for p in plans]}")
                else:
                    print(f"[RAG] WARNING: No {plan_category} plans found in results, using original")

        # 컨텍스트 생성 (OTT면 조합 옵션 포함)
        context = self.build_context(plans, combo_options, is_ott_related)

        # 정렬/필터 정보가 있으면 컨텍스트에 힌트 추가
        if category_hint:
            context = category_hint + context
        if sort_by == "price" and sort_order == "asc" and plans:
            context = f"[가격순 정렬됨 - 첫 번째가 최저가]\n\n{context}"
        elif sort_by == "price" and sort_order == "desc" and plans:
            context = f"[가격순 정렬됨 - 첫 번째가 최고가]\n\n{context}"

        return plans, context


# 싱글톤 인스턴스
rag_service = RAGService()
