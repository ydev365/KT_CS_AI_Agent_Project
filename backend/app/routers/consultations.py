from fastapi import APIRouter, HTTPException
from ..schemas.consultation import ConversationLog, AIAnalysis, ConsultationResponse
from ..services import consultation_service

router = APIRouter(prefix="/api/consultations", tags=["consultations"])


@router.get("/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(consultation_id: str):
    """상담 ID로 전체 상담 정보 조회 (대화 로그 + AI 분석)"""
    result = consultation_service.get_consultation(consultation_id)
    if not result:
        raise HTTPException(status_code=404, detail="상담 정보를 찾을 수 없습니다")
    return result


@router.get("/{consultation_id}/conversation", response_model=ConversationLog)
async def get_conversation(consultation_id: str):
    """상담 ID로 대화 로그 조회"""
    result = consultation_service.get_conversation_log(consultation_id)
    if not result:
        raise HTTPException(status_code=404, detail="대화 로그를 찾을 수 없습니다")
    return result


@router.get("/{consultation_id}/analysis", response_model=AIAnalysis)
async def get_analysis(consultation_id: str):
    """상담 ID로 AI 분석 결과 조회"""
    result = consultation_service.get_ai_analysis(consultation_id)
    if not result:
        raise HTTPException(status_code=404, detail="AI 분석 결과를 찾을 수 없습니다")
    return result


@router.get("/customer/{customer_id}/latest", response_model=ConsultationResponse)
async def get_latest_by_customer(customer_id: str):
    """고객 ID로 최신 상담 정보 조회"""
    result = consultation_service.get_latest_consultation_by_customer(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="해당 고객의 상담 정보를 찾을 수 없습니다")
    return result
