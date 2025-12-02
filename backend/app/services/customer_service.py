from typing import Optional
from ..schemas.customer import CustomerInfo
from .sample_data import SAMPLE_CUSTOMERS


def get_customer(customer_id: str) -> Optional[CustomerInfo]:
    """고객 ID로 고객 정보 조회"""
    data = SAMPLE_CUSTOMERS.get(customer_id)
    if not data:
        return None
    return CustomerInfo(**data)


def get_customer_by_phone(phone: str) -> Optional[CustomerInfo]:
    """전화번호로 고객 정보 조회"""
    for customer_data in SAMPLE_CUSTOMERS.values():
        if customer_data.get("phone") == phone:
            return CustomerInfo(**customer_data)
    return None
