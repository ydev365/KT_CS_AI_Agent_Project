from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..services.session_service import session_service
from ..services.summary_service import summary_service, ConversationSummary
from ..services.recommendation_service import recommendation_service, PlanRecommendation

router = APIRouter(prefix="/api/summary", tags=["summary"])


class SummaryResponse(BaseModel):
    """요약 및 추천 응답"""
    session_id: str
    summary: ConversationSummary
    recommended_plans: List[PlanRecommendation]


@router.get("/{session_id}", response_model=SummaryResponse)
async def get_summary_and_recommendations(session_id: str):
    """
    대화 요약 및 요금제 추천 조회

    - 상담 종료 후 호출
    - 대화 내용 요약 + 3가지 추천 요금제 반환
    """
    # 세션 확인
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    # 대화 기록 조회
    conversation = session_service.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=400, detail="대화 기록이 없습니다.")

    # 고객 정보
    customer_info = session.customer_info.model_dump()

    try:
        # 대화 요약 생성
        summary = await summary_service.summarize_conversation(
            conversation=conversation,
            customer_info=customer_info
        )

        # 대화 기록을 스코어링용 형식으로 변환
        conversation_for_scoring = []
        for msg in conversation:
            speaker = 'customer' if msg.get('role') == 'user' else 'agent'
            conversation_for_scoring.append({
                'speaker': speaker,
                'content': msg.get('content', '')
            })

        # 요금제 추천 생성 (스코어링 기반)
        recommendations = await recommendation_service.generate_recommendations(
            summary=summary,
            customer_info=customer_info,
            target_categories=session.customer_info.target_categories,
            conversation_history=conversation_for_scoring
        )

        return SummaryResponse(
            session_id=session_id,
            summary=summary,
            recommended_plans=recommendations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 생성 중 오류: {str(e)}")


@router.get("/{session_id}/summary-only", response_model=ConversationSummary)
async def get_summary_only(session_id: str):
    """대화 요약만 조회"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    conversation = session_service.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=400, detail="대화 기록이 없습니다.")

    customer_info = session.customer_info.model_dump()

    summary = await summary_service.summarize_conversation(
        conversation=conversation,
        customer_info=customer_info
    )

    return summary


@router.get("/{session_id}/recommendations-only", response_model=List[PlanRecommendation])
async def get_recommendations_only(session_id: str):
    """요금제 추천만 조회"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    conversation = session_service.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=400, detail="대화 기록이 없습니다.")

    customer_info = session.customer_info.model_dump()

    # 먼저 요약 생성
    summary = await summary_service.summarize_conversation(
        conversation=conversation,
        customer_info=customer_info
    )

    # 대화 기록을 스코어링용 형식으로 변환
    conversation_for_scoring = []
    for msg in conversation:
        speaker = 'customer' if msg.get('role') == 'user' else 'agent'
        conversation_for_scoring.append({
            'speaker': speaker,
            'content': msg.get('content', '')
        })

    # 추천 생성 (스코어링 기반)
    recommendations = await recommendation_service.generate_recommendations(
        summary=summary,
        customer_info=customer_info,
        target_categories=session.customer_info.target_categories,
        conversation_history=conversation_for_scoring
    )

    return recommendations
