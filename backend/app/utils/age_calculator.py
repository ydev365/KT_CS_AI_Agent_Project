from datetime import datetime, date
from typing import List, Optional


def calculate_age(birth_date: str) -> int:
    """
    생년월일로 만 나이 계산

    Args:
        birth_date: YYYYMMDD 또는 YYYY-MM-DD 형식

    Returns:
        만 나이
    """
    # 하이픈 제거
    birth_date = birth_date.replace("-", "")

    if len(birth_date) != 8:
        raise ValueError("생년월일은 YYYYMMDD 형식이어야 합니다")

    birth_year = int(birth_date[:4])
    birth_month = int(birth_date[4:6])
    birth_day = int(birth_date[6:8])

    today = date.today()
    age = today.year - birth_year

    # 생일이 지나지 않았으면 1살 빼기
    if (today.month, today.day) < (birth_month, birth_day):
        age -= 1

    return age


def determine_target_categories(age: int, is_foreigner: bool = False, is_disabled: bool = False) -> List[str]:
    """
    나이와 추가 정보를 기반으로 적용 가능한 타겟 카테고리 결정

    Args:
        age: 만 나이
        is_foreigner: 외국인 여부
        is_disabled: 장애인 여부

    Returns:
        적용 가능한 타겟 카테고리 리스트
    """
    categories = ["전체"]  # 모든 고객은 '전체' 요금제 가입 가능

    # 나이 기반 카테고리
    if age <= 12:
        categories.append("만 12세 이하")
    if age <= 18:
        categories.append("만 18세 이하")
    if age <= 34:
        categories.append("만 34세 이하")
    if age >= 65:
        categories.append("만 65세 이상")
    if age >= 75:
        categories.append("만 75세 이상")
    if age >= 80:
        categories.append("만 80세 이상")

    # 특수 카테고리
    if is_foreigner:
        categories.append("외국인 전용")
    if is_disabled:
        categories.append("장애인 전용")

    return categories


def get_primary_target_category(age: int, is_foreigner: bool = False, is_disabled: bool = False) -> str:
    """
    가장 적합한 타겟 카테고리 반환 (상담 시 주로 사용)

    Returns:
        주요 타겟 카테고리 (가장 특화된 것)
    """
    if is_foreigner:
        return "외국인 전용"
    if is_disabled:
        return "장애인 전용"
    if age <= 12:
        return "만 12세 이하"
    if age <= 18:
        return "만 18세 이하"
    if age <= 34:
        return "만 34세 이하"
    if age >= 80:
        return "만 80세 이상"
    if age >= 75:
        return "만 75세 이상"
    if age >= 65:
        return "만 65세 이상"

    return "전체"


def is_target_eligible(plan_target: str, customer_categories: List[str]) -> bool:
    """
    고객이 특정 요금제의 타겟에 해당하는지 확인

    Args:
        plan_target: 요금제의 타겟 (예: "만 34세 이하")
        customer_categories: 고객이 해당하는 카테고리 리스트

    Returns:
        가입 가능 여부
    """
    if not plan_target or plan_target == "전체":
        return True

    return plan_target in customer_categories
