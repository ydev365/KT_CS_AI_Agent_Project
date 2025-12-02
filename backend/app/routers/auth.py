from fastapi import APIRouter, HTTPException
from ..schemas.auth import AuthRequest, AuthResult, SessionInfo
from ..services.auth_service import auth_service
from ..services.session_service import session_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/verify", response_model=AuthResult)
async def verify_customer(request: AuthRequest):
    """
    고객 인증

    - 전화번호와 생년월일로 고객 확인
    - 자사 고객: 상세 정보 반환
    - 타사 고객: 나이 기반 타겟 카테고리만 반환
    """
    try:
        result = auth_service.verify_customer(request)

        # 세션 생성
        session_service.create_session(result.session_id, result)

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인증 처리 중 오류 발생: {str(e)}")


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """세션 정보 조회"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    return session


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """세션 종료"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

    session_service.update_session_status(session_id, "ended")
    return {"message": "세션이 종료되었습니다", "session_id": session_id}
