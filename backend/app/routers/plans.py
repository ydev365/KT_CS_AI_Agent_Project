from fastapi import APIRouter, Query
from typing import List, Optional
from ..schemas.plan import PlanSearchResponse
from ..services import plan_service

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("/search", response_model=PlanSearchResponse)
async def search_plans(
    query: Optional[str] = Query(None, description="검색 키워드"),
    filters: Optional[str] = Query(None, description="필터 (쉼표로 구분: all,youth,teen,senior,junior,disabled,foreigner,addon)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    pageSize: int = Query(100, ge=1, le=200, description="페이지 크기")
):
    """요금제 검색"""
    filter_list = None
    if filters:
        filter_list = [f.strip() for f in filters.split(",")]

    return plan_service.search_plans(
        query=query,
        filters=filter_list,
        page=page,
        page_size=pageSize
    )
