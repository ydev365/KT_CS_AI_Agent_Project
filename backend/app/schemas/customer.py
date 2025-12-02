from pydantic import BaseModel
from typing import List, Optional


class CustomerService(BaseModel):
    type: str
    name: str


class CustomerInfo(BaseModel):
    customerId: str
    name: str
    phone: str
    gender: str
    birthDate: str
    age: int
    isKtMember: bool
    membershipGrade: str
    ktJoinDate: str
    loyaltyYears: int
    currentPlan: str
    currentPlanStartDate: str
    monthlyFee: int
    services: List[CustomerService]
    totalMonthlyFee: int
    familyMembers: int
