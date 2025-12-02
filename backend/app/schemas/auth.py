from pydantic import BaseModel, Field
from typing import Optional, List


class AuthRequest(BaseModel):
    """고객 인증 요청"""
    phone: str = Field(..., description="전화번호 (하이픈 없이)", example="01012345678")
    birth_date: str = Field(..., description="생년월일 (YYYYMMDD)", example="19950315")


class CustomerService(BaseModel):
    """고객 이용 서비스"""
    type: str
    name: str


class AuthResult(BaseModel):
    """고객 인증 결과"""
    success: bool
    is_kt_customer: bool = Field(..., description="KT 자사 고객 여부")
    session_id: str = Field(..., description="상담 세션 ID")

    # 고객 정보 (자사 고객만)
    customer_id: Optional[str] = None
    name: Optional[str] = None
    phone: str
    age: int
    birth_date: str

    # 타겟 카테고리
    target_categories: List[str] = Field(..., description="적용 가능한 요금제 타겟 리스트")
    primary_target: str = Field(..., description="주요 타겟 카테고리")

    # KT 고객 정보 (자사 고객만)
    current_plan: Optional[str] = None
    monthly_fee: Optional[int] = None
    membership_grade: Optional[str] = None
    kt_join_date: Optional[str] = None
    loyalty_years: Optional[int] = None
    family_members: Optional[int] = None
    services: Optional[List[CustomerService]] = None
    total_monthly_fee: Optional[int] = None


class SessionInfo(BaseModel):
    """세션 정보"""
    session_id: str
    customer_info: AuthResult
    created_at: str
    status: str = "active"  # active, ended
