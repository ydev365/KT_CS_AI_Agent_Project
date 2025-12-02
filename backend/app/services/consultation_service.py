from typing import Optional
from ..schemas.consultation import ConversationLog, AIAnalysis, ConsultationResponse
from .sample_data import SAMPLE_CONVERSATIONS, SAMPLE_AI_ANALYSIS


def get_consultation(consultation_id: str) -> Optional[ConsultationResponse]:
    """상담 ID로 상담 정보 조회"""
    conversation_data = SAMPLE_CONVERSATIONS.get(consultation_id)
    analysis_data = SAMPLE_AI_ANALYSIS.get(consultation_id)

    if not conversation_data or not analysis_data:
        return None

    return ConsultationResponse(
        consultation=AIAnalysis(**analysis_data),
        conversation=ConversationLog(**conversation_data)
    )


def get_conversation_log(consultation_id: str) -> Optional[ConversationLog]:
    """상담 ID로 대화 로그 조회"""
    data = SAMPLE_CONVERSATIONS.get(consultation_id)
    if not data:
        return None
    return ConversationLog(**data)


def get_ai_analysis(consultation_id: str) -> Optional[AIAnalysis]:
    """상담 ID로 AI 분석 결과 조회"""
    data = SAMPLE_AI_ANALYSIS.get(consultation_id)
    if not data:
        return None
    return AIAnalysis(**data)


def get_latest_consultation_by_customer(customer_id: str) -> Optional[ConsultationResponse]:
    """고객 ID로 최신 상담 정보 조회"""
    # 샘플 데이터에서 해당 고객의 상담 찾기
    for cons_id, conv_data in SAMPLE_CONVERSATIONS.items():
        if conv_data.get("customerId") == customer_id:
            return get_consultation(cons_id)
    return None
