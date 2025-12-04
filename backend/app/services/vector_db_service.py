import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI
from typing import List, Dict, Any, Optional
import os

from ..core.config import settings
from ..utils.csv_loader import (
    load_plans_csv, plan_to_document, get_plan_metadata,
    load_addon_services_csv, addon_service_to_document, get_addon_service_metadata
)


class VectorDBService:
    _instance: Optional["VectorDBService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _initialize(self):
        if self._initialized:
            return

        # OpenAI 클라이언트
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)

        # ChromaDB 클라이언트 (영속성 저장)
        persist_dir = os.path.abspath(settings.CHROMA_PERSIST_DIR)
        os.makedirs(persist_dir, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        # 요금제 컬렉션
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "KT 요금제 정보"}
        )

        # 부가서비스 컬렉션
        self.addon_collection = self.chroma_client.get_or_create_collection(
            name=f"{settings.CHROMA_COLLECTION_NAME}_addons",
            metadata={"description": "KT OTT 부가서비스 정보"}
        )

        self._initialized = True

    def initialize(self):
        """명시적 초기화"""
        self._initialize()

    def get_embedding(self, text: str) -> List[float]:
        """OpenAI 임베딩 생성"""
        response = self.openai.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def load_plans_from_csv(self, csv_path: Optional[str] = None) -> int:
        """
        CSV에서 요금제 데이터를 로드하여 벡터 DB에 저장

        Returns:
            저장된 요금제 수
        """
        self._initialize()

        csv_path = csv_path or settings.PLANS_CSV_PATH
        plans = load_plans_csv(csv_path)

        # 기존 데이터 삭제 (재초기화)
        existing = self.collection.count()
        if existing > 0:
            # 모든 ID 가져와서 삭제
            all_ids = self.collection.get()["ids"]
            if all_ids:
                self.collection.delete(ids=all_ids)

        # 새 데이터 추가
        documents = []
        metadatas = []
        ids = []
        embeddings = []

        for idx, plan in enumerate(plans):
            doc = plan_to_document(plan)
            documents.append(doc)
            metadatas.append(get_plan_metadata(plan))
            ids.append(f"plan_{idx}")

            # 임베딩 생성
            embedding = self.get_embedding(doc)
            embeddings.append(embedding)

        # 벡터 DB에 저장
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

        return len(plans)

    def load_addon_services_from_csv(self, csv_path: Optional[str] = None) -> int:
        """
        CSV에서 부가서비스 데이터를 로드하여 벡터 DB에 저장

        Returns:
            저장된 부가서비스 수
        """
        self._initialize()

        csv_path = csv_path or settings.ADDON_SERVICES_CSV_PATH
        services = load_addon_services_csv(csv_path)

        # 기존 데이터 삭제 (재초기화)
        existing = self.addon_collection.count()
        if existing > 0:
            all_ids = self.addon_collection.get()["ids"]
            if all_ids:
                self.addon_collection.delete(ids=all_ids)

        # 새 데이터 추가
        documents = []
        metadatas = []
        ids = []
        embeddings = []

        for idx, service in enumerate(services):
            doc = addon_service_to_document(service)
            documents.append(doc)
            metadatas.append(get_addon_service_metadata(service))
            ids.append(f"addon_{idx}")

            # 임베딩 생성
            embedding = self.get_embedding(doc)
            embeddings.append(embedding)

        # 벡터 DB에 저장
        self.addon_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

        return len(services)

    def search_addon_services(
        self,
        query: str,
        ott_type: Optional[str] = None,
        top_k: int = 5,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[Dict[str, Any]]:
        """
        부가서비스 검색

        Args:
            query: 검색 쿼리
            ott_type: OTT 종류 필터 (예: "티빙", "넷플릭스")
            top_k: 반환할 결과 수
            sort_by: 정렬 기준 필드
            sort_order: 정렬 순서

        Returns:
            검색된 부가서비스 리스트
        """
        self._initialize()

        query_embedding = self.get_embedding(query)

        results = self.addon_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i]
            document = results["documents"][0][i]
            distance = results["distances"][0][i]

            # OTT 타입 필터링
            if ott_type:
                if ott_type not in str(metadata.get("ott_type", "")):
                    continue

            search_results.append({
                "service_name": metadata.get("service_name"),
                "price": metadata.get("price"),
                "ott_type": metadata.get("ott_type"),
                "document": document,
                "similarity": 1 - distance
            })

        # 정렬 적용
        if sort_by and search_results:
            reverse = (sort_order == "desc")
            search_results.sort(key=lambda x: x.get(sort_by, 0) or 0, reverse=reverse)

        return search_results[:top_k]

    def get_cheapest_addon_by_ott(self, ott_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """OTT 타입별 최저가 부가서비스 조회"""
        self._initialize()

        results = self.addon_collection.get(include=["documents", "metadatas"])

        services = []
        for i in range(len(results["ids"])):
            metadata = results["metadatas"][i]
            # OTT 타입이 있는 것만
            if metadata.get("ott_type"):
                if ott_type and ott_type not in metadata.get("ott_type", ""):
                    continue
                services.append({
                    "service_name": metadata.get("service_name"),
                    "price": metadata.get("price"),
                    "ott_type": metadata.get("ott_type"),
                    "document": results["documents"][i]
                })

        # 가격순 정렬
        services.sort(key=lambda x: x.get("price", 0) or 0)
        return services

    def search(
        self,
        query: str,
        target_categories: Optional[List[str]] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[Dict[str, Any]]:
        """
        유사도 기반 요금제 검색 (필터링 + 정렬 지원)

        Args:
            query: 검색 쿼리
            target_categories: 필터링할 타겟 카테고리 리스트
            top_k: 반환할 결과 수
            filters: 추가 필터 조건 (예: {"has_ott": True})
            sort_by: 정렬 기준 필드 (예: "price")
            sort_order: 정렬 순서 ("asc" 또는 "desc")

        Returns:
            검색된 요금제 리스트
        """
        self._initialize()

        # 쿼리 임베딩 생성
        query_embedding = self.get_embedding(query)

        # 필터링이 있으면 더 많이 가져옴
        fetch_count = top_k * 3 if (target_categories or filters) else top_k

        # 검색 수행
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=fetch_count,
            include=["documents", "metadatas", "distances"]
        )

        # 결과 정리
        search_results = []
        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i]
            document = results["documents"][0][i]
            distance = results["distances"][0][i]

            # 타겟 필터링
            if target_categories:
                plan_target = metadata.get("target", "전체")
                if plan_target != "전체" and plan_target not in target_categories:
                    continue

            # 추가 필터 적용 (예: has_ott, has_unlimited_data)
            if filters:
                skip = False
                for key, value in filters.items():
                    if metadata.get(key) != value:
                        skip = True
                        break
                if skip:
                    continue

            search_results.append({
                "plan_name": metadata.get("plan_name"),
                "price": metadata.get("price"),
                "target": metadata.get("target"),
                "membership": metadata.get("membership"),
                "has_unlimited_data": metadata.get("has_unlimited_data"),
                "has_ott": metadata.get("has_ott"),
                "document": document,
                "similarity": 1 - distance  # 거리를 유사도로 변환
            })

        # 정렬 적용
        if sort_by and search_results:
            reverse = (sort_order == "desc")
            search_results.sort(key=lambda x: x.get(sort_by, 0) or 0, reverse=reverse)

        # top_k 개수만 반환
        return search_results[:top_k]

    def get_all_plans(self) -> List[Dict[str, Any]]:
        """모든 요금제 조회"""
        self._initialize()

        results = self.collection.get(include=["documents", "metadatas"])

        plans = []
        for i in range(len(results["ids"])):
            plans.append({
                "id": results["ids"][i],
                "metadata": results["metadatas"][i],
                "document": results["documents"][i]
            })

        return plans

    def get_plans_by_target(self, target: str) -> List[Dict[str, Any]]:
        """특정 타겟의 요금제 조회"""
        self._initialize()

        results = self.collection.get(
            where={"target": target},
            include=["documents", "metadatas"]
        )

        plans = []
        for i in range(len(results["ids"])):
            plans.append({
                "id": results["ids"][i],
                "metadata": results["metadatas"][i],
                "document": results["documents"][i]
            })

        return plans


# 싱글톤 인스턴스
vector_db_service = VectorDBService()
