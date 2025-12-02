from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime


class ConversationMessage(BaseModel):
    timestamp: str
    speaker: Literal["ai", "customer"]
    speakerId: str
    content: str


class ConversationLog(BaseModel):
    consultationId: str
    customerId: str
    startTime: str
    endTime: Optional[str] = None
    messages: List[ConversationMessage]


class AISummary(BaseModel):
    currentPlan: str
    currentPrice: int
    requestedFeature: str
    customerProfile: str
    mainConcern: str
    opportunity: str


class PlanRecommendation(BaseModel):
    id: int
    name: str
    price: int
    discountedPrice: int
    discount: str
    data: str
    features: List[str]
    badge: Literal["best", "upsell", "budget"]
    comparison: str


class AIAnalysis(BaseModel):
    consultationId: str
    customerId: str
    summary: AISummary
    recommendedPlans: List[PlanRecommendation]


class ConsultationResponse(BaseModel):
    consultation: AIAnalysis
    conversation: ConversationLog
