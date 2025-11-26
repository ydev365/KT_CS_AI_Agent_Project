import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from config import get_settings

settings = get_settings()


class ChromaClient:
    """ChromaDB 클라이언트 래퍼"""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

    def get_collection(self, name: str = "kt_plans"):
        """컬렉션 가져오기 또는 생성"""
        return self.client.get_or_create_collection(
            name=name,
            metadata={"description": "KT 요금제 정보"}
        )

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict]] = None
    ):
        """문서 추가"""
        collection = self.get_collection(collection_name)
        collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5
    ) -> Dict:
        """쿼리 실행"""
        collection = self.get_collection(collection_name)
        return collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

    def get_all(self, collection_name: str) -> Dict:
        """모든 문서 조회"""
        collection = self.get_collection(collection_name)
        return collection.get()

    def delete_collection(self, collection_name: str):
        """컬렉션 삭제"""
        try:
            self.client.delete_collection(collection_name)
        except ValueError:
            pass  # 컬렉션이 없는 경우

    def count(self, collection_name: str) -> int:
        """문서 수 조회"""
        collection = self.get_collection(collection_name)
        return collection.count()
