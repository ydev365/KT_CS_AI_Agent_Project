from fastapi import APIRouter, HTTPException
from ..schemas.customer import CustomerInfo
from ..services import customer_service

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/{customer_id}", response_model=CustomerInfo)
async def get_customer(customer_id: str):
    """고객 ID로 고객 정보 조회"""
    result = customer_service.get_customer(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="고객 정보를 찾을 수 없습니다")
    return result


@router.get("/phone/{phone}", response_model=CustomerInfo)
async def get_customer_by_phone(phone: str):
    """전화번호로 고객 정보 조회"""
    result = customer_service.get_customer_by_phone(phone)
    if not result:
        raise HTTPException(status_code=404, detail="고객 정보를 찾을 수 없습니다")
    return result
