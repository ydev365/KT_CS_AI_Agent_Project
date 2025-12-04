from typing import List, Optional
from ..schemas.plan import PlanSearchResult, PlanSearchResponse
from .rag_service import rag_service


# 퀵 태그 → 검색 쿼리 변환 맵 (CSV target 필드 기준)
TAG_TO_QUERY = {
    'all': '전체',  # 일반 요금제
    'youth': '만 34세 이하 Y 청년',  # Y 요금제 (만 34세 이하)
    'senior': '만 65세 이상 시니어',  # 시니어 요금제
    'junior': '만 12세 이하 주니어',  # 주니어 요금제
    'disabled': '장애인 전용 복지',  # 장애인 전용
    'foreigner': '외국인 전용 웰컴',  # 외국인 전용
    'addon': '부가서비스 OTT 구독',  # 부가서비스
}


def search_plans(
    query: Optional[str] = None,
    filters: Optional[List[str]] = None,
    page: int = 1,
    page_size: int = 10
) -> PlanSearchResponse:
    """요금제 검색 (RAG 기반)"""
    print(f"[PLAN SEARCH] query={query}, filters={filters}")

    # 검색 쿼리 결정
    search_query = query or ""

    # 필터가 있으면 쿼리에 추가
    if filters:
        filter_queries = [TAG_TO_QUERY.get(f, f) for f in filters]
        search_query = f"{search_query} {' '.join(filter_queries)}".strip()

    # 퀵 태그를 검색 쿼리로 변환
    if search_query.lower() in TAG_TO_QUERY:
        search_query = TAG_TO_QUERY[search_query.lower()]

    # 기본 검색어 (빈 쿼리일 때)
    if not search_query:
        search_query = "5G 요금제"

    # RAG 검색
    print(f"[PLAN SEARCH] search_query={search_query}")
    plans, context = rag_service.get_relevant_plans_with_context(
        query=search_query,
        target_categories=None,
        top_k=page_size * page  # 페이지네이션을 위해 더 많이 가져옴
    )
    print(f"[PLAN SEARCH] found {len(plans)} plans")

    results = []
    for i, plan in enumerate(plans):
        # 태그 생성
        tags = []

        if plan.get('has_ott'):
            tags.append({'type': 'popular', 'label': 'OTT 포함'})

        if plan.get('has_unlimited_data'):
            tags.append({'type': 'discount', 'label': '무제한'})

        membership = plan.get('membership')
        if membership and membership != 'None' and membership:
            tags.append({'type': 'new', 'label': membership})

        # 설명 생성
        data_info = plan.get('data_gb', '정보 없음')
        choice_info = plan.get('choice', '')

        description_parts = [f"데이터 {data_info}"]
        if choice_info and choice_info != '없음':
            description_parts.append(f"OTT: {choice_info}")

        description = " | ".join(description_parts)

        # 관련도 점수 (순서 기반, 최대 0.99)
        relevance = max(0.5, 0.99 - (i * 0.05))

        results.append(PlanSearchResult(
            id=str(i + 1),
            title=plan.get('plan_name', '알 수 없음'),
            price=plan.get('price', 0),
            description=description,
            tags=tags,
            relevance=relevance
        ))

    # 페이지네이션
    total_count = len(results)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_results = results[start_idx:end_idx]

    return PlanSearchResponse(
        results=paginated_results,
        totalCount=total_count,
        pageNumber=page,
        pageSize=page_size
    )
