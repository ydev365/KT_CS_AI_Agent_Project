"""
샘플 데이터 - 프론트엔드의 하드코딩된 데이터와 일치
"""

# 고객 정보 샘플 데이터
SAMPLE_CUSTOMERS = {
    "C001": {
        "customerId": "C001",
        "name": "김민수",
        "phone": "010-1234-5678",
        "gender": "남성",
        "birthDate": "1985-03-15",
        "age": 39,
        "isKtMember": True,
        "membershipGrade": "VIP",
        "ktJoinDate": "2018-06-20",
        "loyaltyYears": 6,
        "currentPlan": "5G 베이직",
        "currentPlanStartDate": "2023-01-15",
        "monthlyFee": 55000,
        "services": [
            {"type": "mobile", "name": "5G 모바일"},
            {"type": "internet", "name": "기가인터넷"},
            {"type": "tv", "name": "KT 올레 tv"}
        ],
        "totalMonthlyFee": 89000,
        "familyMembers": 3
    },
    "C002": {
        "customerId": "C002",
        "name": "이영희",
        "phone": "010-9876-5432",
        "gender": "여성",
        "birthDate": "1990-07-22",
        "age": 34,
        "isKtMember": True,
        "membershipGrade": "Gold",
        "ktJoinDate": "2020-03-10",
        "loyaltyYears": 4,
        "currentPlan": "5G 스탠다드",
        "currentPlanStartDate": "2023-06-01",
        "monthlyFee": 69000,
        "services": [
            {"type": "mobile", "name": "5G 모바일"}
        ],
        "totalMonthlyFee": 69000,
        "familyMembers": 1
    }
}

# 상담 대화 로그 샘플 데이터
SAMPLE_CONVERSATIONS = {
    "CONS001": {
        "consultationId": "CONS001",
        "customerId": "C001",
        "startTime": "2024-01-15T14:30:00",
        "endTime": "2024-01-15T14:38:00",
        "messages": [
            {
                "timestamp": "2024-01-15T14:30:00",
                "speaker": "ai",
                "speakerId": "AI 상담사",
                "content": "안녕하세요, KT AI 상담사입니다. 무엇을 도와드릴까요?"
            },
            {
                "timestamp": "2024-01-15T14:30:30",
                "speaker": "customer",
                "speakerId": "고객_010-1234-5678",
                "content": "네, 지금 쓰고 있는 요금제가 데이터가 너무 부족해서요. 더 많은 데이터를 쓸 수 있는 요금제로 바꾸고 싶어요."
            },
            {
                "timestamp": "2024-01-15T14:31:00",
                "speaker": "ai",
                "speakerId": "AI 상담사",
                "content": "네, 고객님. 현재 5G 베이직 요금제를 사용 중이시네요. 월 55,000원에 데이터 50GB를 제공받고 계십니다. 데이터를 더 많이 사용하시고 싶으시다면 몇 가지 좋은 옵션이 있습니다."
            },
            {
                "timestamp": "2024-01-15T14:31:45",
                "speaker": "customer",
                "speakerId": "고객_010-1234-5678",
                "content": "어떤 옵션이 있나요? 가격대는 어느 정도인가요?"
            },
            {
                "timestamp": "2024-01-15T14:32:30",
                "speaker": "ai",
                "speakerId": "AI 상담사",
                "content": "고객님께서 가족 3분이 KT를 이용 중이시라서 가족 결합 할인을 받으실 수 있습니다. 5G 슈퍼플랜의 경우 원래 75,000원인데, 가족 결합 20% 할인을 적용하면 60,000원에 150GB 데이터를 사용하실 수 있어요."
            },
            {
                "timestamp": "2024-01-15T14:33:15",
                "speaker": "customer",
                "speakerId": "고객_010-1234-5678",
                "content": "오, 그거 괜찮네요. 다른 옵션도 있나요?"
            },
            {
                "timestamp": "2024-01-15T14:34:00",
                "speaker": "ai",
                "speakerId": "AI 상담사",
                "content": "네, 만약 데이터 걱정 없이 무제한으로 사용하고 싶으시다면 5G 프리미엄 요금제가 있습니다. 월 89,000원이지만 가족 결합 시 71,200원에 데이터 무제한과 프리미엄 혜택들을 받으실 수 있어요. 혹시 더 저렴한 옵션을 원하시면 5G 라이트플러스도 있는데, 49,000원에 80GB를 제공합니다."
            },
            {
                "timestamp": "2024-01-15T14:35:00",
                "speaker": "customer",
                "speakerId": "고객_010-1234-5678",
                "content": "음... 5G 슈퍼플랜이 가장 적당한 것 같아요. 150GB면 충분할 것 같고, 가격도 괜찮네요."
            },
            {
                "timestamp": "2024-01-15T14:35:30",
                "speaker": "ai",
                "speakerId": "AI 상담사",
                "content": "좋은 선택이세요! 5G 슈퍼플랜으로 변경하시면 현재보다 월 5,000원 추가로 데이터를 3배 더 사용하실 수 있습니다. 지금 바로 변경 도와드릴까요?"
            },
            {
                "timestamp": "2024-01-15T14:36:00",
                "speaker": "customer",
                "speakerId": "고객_010-1234-5678",
                "content": "네, 그런데 혹시 상담사분과 직접 통화해서 자세한 내용 확인하고 싶은데 가능할까요?"
            },
            {
                "timestamp": "2024-01-15T14:36:30",
                "speaker": "ai",
                "speakerId": "AI 상담사",
                "content": "물론이죠! 지금 바로 전문 상담사에게 연결해 드리겠습니다. 상담사에게 고객님의 요청 사항과 추천 요금제 정보를 전달해 드릴게요. 잠시만 기다려 주세요."
            }
        ]
    }
}

# AI 분석 결과 샘플 데이터
SAMPLE_AI_ANALYSIS = {
    "CONS001": {
        "consultationId": "CONS001",
        "customerId": "C001",
        "summary": {
            "currentPlan": "5G 베이직",
            "currentPrice": 55000,
            "requestedFeature": "더 많은 데이터 (100GB+)",
            "customerProfile": "가족 3명 KT 이용 중",
            "mainConcern": "데이터 부족",
            "opportunity": "가족 결합 할인 가능"
        },
        "recommendedPlans": [
            {
                "id": 1,
                "name": "5G 슈퍼플랜",
                "price": 75000,
                "discountedPrice": 60000,
                "discount": "가족 3명 20%",
                "data": "150GB",
                "features": ["데이터 쉐어링", "멤버십 VIP", "로밍 50% 할인"],
                "badge": "best",
                "comparison": "현재 대비 +5,000원으로 데이터 3배"
            },
            {
                "id": 2,
                "name": "5G 프리미엄",
                "price": 89000,
                "discountedPrice": 71200,
                "discount": "가족 3명 20%",
                "data": "무제한",
                "features": ["데이터 무제한", "해외로밍 무료", "구독 서비스 포함"],
                "badge": "upsell",
                "comparison": "프리미엄 혜택 + 데이터 무제한"
            },
            {
                "id": 3,
                "name": "5G 라이트플러스",
                "price": 49000,
                "discountedPrice": 49000,
                "discount": "결합 할인 미적용",
                "data": "80GB",
                "features": ["기본 데이터 80GB", "표준 멤버십"],
                "badge": "budget",
                "comparison": "현재 대비 -6,000원, 데이터 +30GB"
            }
        ]
    }
}

# 요금제 목록 샘플 데이터
SAMPLE_PLANS = [
    {
        "id": "plan_001",
        "title": "5G 슈퍼플랜",
        "price": 75000,
        "description": "데이터 150GB + 다양한 혜택이 포함된 인기 요금제",
        "tags": [
            {"type": "popular", "label": "인기"},
            {"type": "discount", "label": "가족결합 20%"}
        ],
        "category": ["5g", "family"],
        "relevance": 0.95
    },
    {
        "id": "plan_002",
        "title": "5G 프리미엄",
        "price": 89000,
        "description": "데이터 무제한 + 프리미엄 혜택 총집합",
        "tags": [
            {"type": "popular", "label": "프리미엄"},
            {"type": "discount", "label": "가족결합 20%"}
        ],
        "category": ["5g", "unlimited", "family"],
        "relevance": 0.90
    },
    {
        "id": "plan_003",
        "title": "5G 베이직",
        "price": 55000,
        "description": "기본에 충실한 5G 입문 요금제 (50GB)",
        "tags": [
            {"type": "other", "label": "입문"}
        ],
        "category": ["5g"],
        "relevance": 0.70
    },
    {
        "id": "plan_004",
        "title": "5G 라이트플러스",
        "price": 49000,
        "description": "합리적인 가격의 5G 요금제 (80GB)",
        "tags": [
            {"type": "discount", "label": "알뜰"}
        ],
        "category": ["5g"],
        "relevance": 0.75
    },
    {
        "id": "plan_005",
        "title": "청년 5G 스페셜",
        "price": 45000,
        "description": "만 34세 이하 청년 전용 5G 요금제",
        "tags": [
            {"type": "new", "label": "청년전용"},
            {"type": "discount", "label": "30% 할인"}
        ],
        "category": ["5g", "youth"],
        "relevance": 0.85
    },
    {
        "id": "plan_006",
        "title": "시니어 케어 요금제",
        "price": 35000,
        "description": "65세 이상 시니어를 위한 맞춤 요금제",
        "tags": [
            {"type": "other", "label": "시니어"},
            {"type": "discount", "label": "특별할인"}
        ],
        "category": ["senior"],
        "relevance": 0.80
    },
    {
        "id": "plan_007",
        "title": "패밀리 결합 무제한",
        "price": 99000,
        "description": "온 가족이 함께 쓰는 무제한 요금제",
        "tags": [
            {"type": "popular", "label": "가족추천"},
            {"type": "discount", "label": "최대 40% 할인"}
        ],
        "category": ["5g", "family", "unlimited"],
        "relevance": 0.92
    },
    {
        "id": "plan_008",
        "title": "데이터 ON 요금제",
        "price": 65000,
        "description": "데이터 중심 사용자를 위한 요금제 (200GB)",
        "tags": [
            {"type": "new", "label": "신규"}
        ],
        "category": ["5g"],
        "relevance": 0.78
    }
]
