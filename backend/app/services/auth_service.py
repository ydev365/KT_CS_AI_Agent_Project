import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from ..schemas.auth import AuthRequest, AuthResult, CustomerService
from ..utils.age_calculator import calculate_age, determine_target_categories, get_primary_target_category


# 샘플 고객 데이터 (테스트용)
SAMPLE_CUSTOMERS: Dict[str, Dict[str, Any]] = {
    # 자사 고객 - Y요금제 대상 (만 34세 이하)
    "01012345678": {
        "customer_id": "C001",
        "name": "김민수",
        "birth_date": "19950315",
        "is_kt_customer": True,
        "current_plan": "5G 슬림 14GB",
        "monthly_fee": 55000,
        "membership_grade": "VIP",
        "kt_join_date": "2018-06-20",
        "loyalty_years": 6,
        "family_members": 2,
        "services": [
            {"type": "mobile", "name": "5G 모바일"},
            {"type": "internet", "name": "기가인터넷"}
        ],
        "total_monthly_fee": 89000
    },
    # 자사 고객 - 시니어 대상 (만 65세 이상)
    "01098765432": {
        "customer_id": "C002",
        "name": "박영순",
        "birth_date": "19550722",
        "is_kt_customer": True,
        "current_plan": "5G 시니어 베이직",
        "monthly_fee": 49000,
        "membership_grade": "Gold",
        "kt_join_date": "2015-03-10",
        "loyalty_years": 9,
        "family_members": 1,
        "services": [
            {"type": "mobile", "name": "5G 모바일"},
            {"type": "tv", "name": "올레 TV"}
        ],
        "total_monthly_fee": 72000
    },
    # 자사 고객 - 일반 (35~64세)
    "01011112222": {
        "customer_id": "C003",
        "name": "이철호",
        "birth_date": "19800515",
        "is_kt_customer": True,
        "current_plan": "5G 베이직",
        "monthly_fee": 80000,
        "membership_grade": "VIP",
        "kt_join_date": "2010-01-15",
        "loyalty_years": 14,
        "family_members": 4,
        "services": [
            {"type": "mobile", "name": "5G 모바일"},
            {"type": "internet", "name": "기가인터넷"},
            {"type": "tv", "name": "올레 TV"}
        ],
        "total_monthly_fee": 145000
    },
    # 자사 고객 - Y틴 대상 (만 18세 이하)
    "01033334444": {
        "customer_id": "C004",
        "name": "김지우",
        "birth_date": "20100510",
        "is_kt_customer": True,
        "current_plan": "5G Y틴",
        "monthly_fee": 47000,
        "membership_grade": "일반",
        "kt_join_date": "2023-03-01",
        "loyalty_years": 1,
        "family_members": 3,
        "services": [
            {"type": "mobile", "name": "5G 모바일"}
        ],
        "total_monthly_fee": 47000
    }
}


class AuthService:
    def verify_customer(self, request: AuthRequest) -> AuthResult:
        """
        고객 인증 및 정보 조회

        Args:
            request: 전화번호, 생년월일

        Returns:
            인증 결과 및 고객 정보
        """
        phone = request.phone.replace("-", "")
        birth_date = request.birth_date.replace("-", "")

        # 세션 ID 생성
        session_id = str(uuid.uuid4())

        # 나이 계산
        try:
            age = calculate_age(birth_date)
        except ValueError as e:
            raise ValueError(f"생년월일 형식이 올바르지 않습니다: {e}")

        # 타겟 카테고리 결정
        target_categories = determine_target_categories(age)
        primary_target = get_primary_target_category(age)

        # 샘플 데이터에서 고객 조회
        customer_data = SAMPLE_CUSTOMERS.get(phone)

        if customer_data:
            # 자사 고객
            # 생년월일 일치 확인
            if customer_data["birth_date"] != birth_date:
                # 생년월일 불일치 - 타사 고객으로 처리
                return AuthResult(
                    success=True,
                    is_kt_customer=False,
                    session_id=session_id,
                    phone=phone,
                    age=age,
                    birth_date=birth_date,
                    target_categories=target_categories,
                    primary_target=primary_target
                )

            # 자사 고객 정보 반환
            services = [
                CustomerService(**s) for s in customer_data.get("services", [])
            ]

            return AuthResult(
                success=True,
                is_kt_customer=True,
                session_id=session_id,
                customer_id=customer_data["customer_id"],
                name=customer_data["name"],
                phone=phone,
                age=age,
                birth_date=birth_date,
                target_categories=target_categories,
                primary_target=primary_target,
                current_plan=customer_data.get("current_plan"),
                monthly_fee=customer_data.get("monthly_fee"),
                membership_grade=customer_data.get("membership_grade"),
                kt_join_date=customer_data.get("kt_join_date"),
                loyalty_years=customer_data.get("loyalty_years"),
                family_members=customer_data.get("family_members"),
                services=services,
                total_monthly_fee=customer_data.get("total_monthly_fee")
            )
        else:
            # 타사 고객
            return AuthResult(
                success=True,
                is_kt_customer=False,
                session_id=session_id,
                phone=phone,
                age=age,
                birth_date=birth_date,
                target_categories=target_categories,
                primary_target=primary_target
            )


# 싱글톤 인스턴스
auth_service = AuthService()
