import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..core.redis_client import redis_client
from ..core.config import settings
from ..schemas.auth import AuthResult, SessionInfo


class SessionService:
    """Redis 기반 세션 관리 서비스"""

    SESSION_PREFIX = "session:"
    CONVERSATION_PREFIX = "conversation:"

    def _get_session_key(self, session_id: str) -> str:
        return f"{self.SESSION_PREFIX}{session_id}"

    def _get_conversation_key(self, session_id: str) -> str:
        return f"{self.CONVERSATION_PREFIX}{session_id}"

    def create_session(self, session_id: str, customer_info: AuthResult) -> SessionInfo:
        """새 상담 세션 생성"""
        session_data = SessionInfo(
            session_id=session_id,
            customer_info=customer_info,
            created_at=datetime.now().isoformat(),
            status="active"
        )

        # Redis에 저장
        expiry_seconds = settings.SESSION_TIMEOUT_MINUTES * 60
        redis_client.set(
            self._get_session_key(session_id),
            session_data.model_dump_json(),
            ex=expiry_seconds
        )

        return session_data

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """세션 정보 조회"""
        data = redis_client.get(self._get_session_key(session_id))
        if not data:
            return None

        try:
            return SessionInfo.model_validate_json(data)
        except Exception:
            return None

    def update_session_status(self, session_id: str, status: str) -> bool:
        """세션 상태 업데이트"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = status
        redis_client.set(
            self._get_session_key(session_id),
            session.model_dump_json(),
            ex=settings.SESSION_TIMEOUT_MINUTES * 60
        )
        return True

    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        redis_client.delete(self._get_session_key(session_id))
        redis_client.delete(self._get_conversation_key(session_id))
        return True

    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """대화 메시지 추가"""
        # 타임스탬프 추가
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        redis_client.rpush(self._get_conversation_key(session_id), message)

        # 세션 만료 시간 갱신
        redis_client.expire(
            self._get_conversation_key(session_id),
            settings.SESSION_TIMEOUT_MINUTES * 60
        )

        return True

    def get_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """대화 기록 조회"""
        messages = redis_client.lrange(
            self._get_conversation_key(session_id),
            0, -1
        )
        return messages

    def extend_session(self, session_id: str) -> bool:
        """세션 만료 시간 연장"""
        expiry_seconds = settings.SESSION_TIMEOUT_MINUTES * 60
        redis_client.expire(self._get_session_key(session_id), expiry_seconds)
        redis_client.expire(self._get_conversation_key(session_id), expiry_seconds)
        return True


# 싱글톤 인스턴스
session_service = SessionService()
