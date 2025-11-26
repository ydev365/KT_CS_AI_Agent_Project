import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from openai import OpenAI
from config import get_settings

settings = get_settings()


class RAGService:
    """ChromaDB 기반 RAG 서비스"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """요금제 컬렉션 가져오기 또는 생성"""
        return self.chroma_client.get_or_create_collection(
            name="kt_plans",
            metadata={"description": "KT 요금제 정보"}
        )

    def add_plan(self, plan_data: Dict) -> str:
        """요금제 정보 추가"""
        plan_id = f"plan_{plan_data['plan_name'].replace(' ', '_')}"

        # 문서 텍스트 생성
        document = self._create_document(plan_data)

        # 메타데이터 준비
        metadata = {
            "plan_name": plan_data.get("plan_name", ""),
            "monthly_fee": plan_data.get("monthly_fee", ""),
            "data_allowance": plan_data.get("data_allowance", ""),
            "target_age": plan_data.get("target_age", "전체"),
        }

        self.collection.upsert(
            ids=[plan_id],
            documents=[document],
            metadatas=[metadata]
        )
        return plan_id

    def _create_document(self, plan_data: Dict) -> str:
        """요금제 정보를 검색 가능한 문서로 변환"""
        parts = [
            f"요금제명: {plan_data.get('plan_name', '')}",
            f"월정액: {plan_data.get('monthly_fee', '')}",
            f"데이터: {plan_data.get('data_allowance', '')}",
            f"통화: {plan_data.get('call_allowance', '기본 제공')}",
            f"문자: {plan_data.get('text_allowance', '기본 제공')}",
            f"대상: {plan_data.get('target_age', '전체')}",
            f"혜택: {plan_data.get('benefits', '')}",
            f"부가서비스: {plan_data.get('additional_services', '')}",
        ]
        return "\n".join(parts)

    def search_plans(self, query: str, n_results: int = 5) -> List[Dict]:
        """쿼리로 관련 요금제 검색"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        plans = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                plans.append({
                    "document": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
        return plans

    def get_context_for_query(self, query: str) -> str:
        """쿼리에 대한 컨텍스트 생성"""
        plans = self.search_plans(query, n_results=5)
        if not plans:
            return "관련 요금제 정보를 찾을 수 없습니다."

        context_parts = ["[관련 KT 요금제 정보]"]
        for i, plan in enumerate(plans, 1):
            context_parts.append(f"\n--- 요금제 {i} ---")
            context_parts.append(plan['document'])

        return "\n".join(context_parts)

    def get_all_plans(self) -> List[Dict]:
        """모든 요금제 조회"""
        results = self.collection.get()
        plans = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents']):
                plans.append({
                    "id": results['ids'][i],
                    "document": doc,
                    "metadata": results['metadatas'][i] if results['metadatas'] else {}
                })
        return plans

    def clear_collection(self):
        """컬렉션 초기화 (주의: 모든 데이터 삭제)"""
        self.chroma_client.delete_collection("kt_plans")
        self.collection = self._get_or_create_collection()

    def get_existing_plan_names(self) -> set:
        """이미 저장된 요금제 이름 목록 반환"""
        results = self.collection.get()
        existing_names = set()
        if results and results['metadatas']:
            for metadata in results['metadatas']:
                if metadata and 'plan_name' in metadata:
                    existing_names.add(metadata['plan_name'])
        return existing_names
