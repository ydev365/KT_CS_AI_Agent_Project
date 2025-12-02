from typing import List, Dict, Any, Optional
from .vector_db_service import vector_db_service


class RAGService:
    """RAG (Retrieval-Augmented Generation) 서비스"""

    def __init__(self):
        self.vector_db = vector_db_service

    def search_plans(
        self,
        query: str,
        target_categories: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        고객 질문에 맞는 요금제 검색

        Args:
            query: 검색 쿼리
            target_categories: 고객이 해당하는 타겟 카테고리 리스트
            top_k: 반환할 결과 수

        Returns:
            검색된 요금제 리스트
        """
        return self.vector_db.search(
            query=query,
            target_categories=target_categories,
            top_k=top_k
        )

    def build_context(self, plans: List[Dict[str, Any]]) -> str:
        """
        검색된 요금제로 LLM 컨텍스트 생성

        Args:
            plans: 검색된 요금제 리스트

        Returns:
            LLM에 제공할 컨텍스트 문자열
        """
        if not plans:
            return "검색된 요금제가 없습니다."

        context_parts = [
            "[검색된 요금제 정보]",
            "※ 아래 정보를 꼼꼼히 읽고 각 요금제의 차이점을 파악하세요.",
            "※ 고객이 비교를 요청하면 모든 항목을 비교해서 다른 점을 설명하세요."
        ]

        for i, plan in enumerate(plans, 1):
            context_parts.append(f"\n{'='*40}")
            context_parts.append(f"【요금제 {i}】")
            context_parts.append(f"{'='*40}")
            context_parts.append(plan["document"])

        return "\n".join(context_parts)

    def get_relevant_plans_with_context(
        self,
        query: str,
        target_categories: Optional[List[str]] = None,
        top_k: int = 5
    ) -> tuple[List[Dict[str, Any]], str]:
        """
        요금제 검색 및 컨텍스트 생성

        Returns:
            (검색된 요금제 리스트, LLM 컨텍스트)
        """
        plans = self.search_plans(query, target_categories, top_k)
        context = self.build_context(plans)
        return plans, context


# 싱글톤 인스턴스
rag_service = RAGService()
