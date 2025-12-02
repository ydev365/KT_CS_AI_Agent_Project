import redis
import json
from typing import Optional, Any
from .config import settings


class RedisClient:
    _instance: Optional["RedisClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """값 저장 (ex: 만료 시간(초))"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return self.client.set(key, value, ex=ex)

    def get(self, key: str) -> Optional[str]:
        """값 조회"""
        return self.client.get(key)

    def get_json(self, key: str) -> Optional[Any]:
        """JSON 값 조회"""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    def delete(self, key: str) -> int:
        """키 삭제"""
        return self.client.delete(key)

    def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        return self.client.exists(key) > 0

    def expire(self, key: str, seconds: int) -> bool:
        """만료 시간 설정"""
        return self.client.expire(key, seconds)

    def lpush(self, key: str, value: Any) -> int:
        """리스트 왼쪽에 추가"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return self.client.lpush(key, value)

    def rpush(self, key: str, value: Any) -> int:
        """리스트 오른쪽에 추가"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return self.client.rpush(key, value)

    def lrange(self, key: str, start: int, end: int) -> list:
        """리스트 범위 조회"""
        values = self.client.lrange(key, start, end)
        result = []
        for v in values:
            try:
                result.append(json.loads(v))
            except json.JSONDecodeError:
                result.append(v)
        return result

    def ping(self) -> bool:
        """연결 확인"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False


# 싱글톤 인스턴스
redis_client = RedisClient()
