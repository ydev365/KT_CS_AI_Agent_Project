from pydantic import BaseModel
from typing import List, Optional, Literal


class PlanTag(BaseModel):
    type: Literal["discount", "popular", "new", "other"]
    label: str


class PlanSearchResult(BaseModel):
    id: str
    title: str
    price: int
    description: str
    tags: List[PlanTag]
    relevance: float


class PlanSearchResponse(BaseModel):
    results: List[PlanSearchResult]
    totalCount: int
    pageNumber: int
    pageSize: int


class PlanSearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[List[str]] = None
    page: int = 1
    pageSize: int = 10
