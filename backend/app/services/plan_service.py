from typing import List, Optional
from ..schemas.plan import PlanSearchResult, PlanSearchResponse
from .sample_data import SAMPLE_PLANS


def search_plans(
    query: Optional[str] = None,
    filters: Optional[List[str]] = None,
    page: int = 1,
    page_size: int = 10
) -> PlanSearchResponse:
    """요금제 검색"""
    results = []

    for plan in SAMPLE_PLANS:
        relevance = plan["relevance"]
        match = True

        # 쿼리 검색
        if query:
            query_lower = query.lower()
            title_match = query_lower in plan["title"].lower()
            desc_match = query_lower in plan["description"].lower()

            if not (title_match or desc_match):
                match = False
            else:
                # 쿼리 매칭 시 relevance 증가
                if title_match:
                    relevance = min(1.0, relevance + 0.1)

        # 필터 적용
        if filters and match:
            plan_categories = plan.get("category", [])
            # 필터 중 하나라도 매칭되면 포함
            filter_match = any(f in plan_categories for f in filters)
            if not filter_match:
                match = False

        if match:
            results.append(PlanSearchResult(
                id=plan["id"],
                title=plan["title"],
                price=plan["price"],
                description=plan["description"],
                tags=plan["tags"],
                relevance=relevance
            ))

    # relevance 기준 정렬
    results.sort(key=lambda x: x.relevance, reverse=True)

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
