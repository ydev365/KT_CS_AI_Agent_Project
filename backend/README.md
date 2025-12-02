# KT CS AI Agent Backend

KT 고객센터 AI 상담 지원 시스템 백엔드 API 서버입니다.

## 기술 스택

- **Framework**: FastAPI
- **WebSocket**: python-socketio
- **Validation**: Pydantic
- **Server**: Uvicorn

## 설치 및 실행

### 1. 가상환경 생성 (권장)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
# 방법 1: run.py 사용
python run.py

# 방법 2: uvicorn 직접 실행
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
```

서버가 시작되면 다음 URL에서 접근 가능합니다:
- API 서버: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## API 엔드포인트

### 상담 (Consultations)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/consultations/{consultation_id}` | 상담 전체 정보 조회 |
| GET | `/api/consultations/{consultation_id}/conversation` | 대화 로그 조회 |
| GET | `/api/consultations/{consultation_id}/analysis` | AI 분석 결과 조회 |
| GET | `/api/consultations/customer/{customer_id}/latest` | 고객의 최신 상담 조회 |

### 고객 (Customers)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/customers/{customer_id}` | 고객 ID로 정보 조회 |
| GET | `/api/customers/phone/{phone}` | 전화번호로 정보 조회 |

### 요금제 (Plans)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/plans/search` | 요금제 검색 |

#### 요금제 검색 파라미터
- `query`: 검색 키워드 (선택)
- `filters`: 필터 (쉼표 구분: youth, family, 5g, senior, unlimited)
- `page`: 페이지 번호 (기본: 1)
- `pageSize`: 페이지 크기 (기본: 10)

### WebSocket 이벤트

#### 클라이언트 → 서버
- `join_consultation`: 상담 세션 참가
- `leave_consultation`: 상담 세션 떠나기

#### 서버 → 클라이언트
- `connection_success`: 연결 성공
- `joined_consultation`: 상담 참가 완료
- `consultation:updated`: 상담 정보 업데이트
- `consultation:message-added`: 새 메시지 추가
- `consultation:status-change`: 상담 상태 변경

## 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 설정
│   ├── websocket_manager.py # Socket.IO 설정
│   ├── routers/             # API 라우터
│   │   ├── consultations.py
│   │   ├── customers.py
│   │   └── plans.py
│   ├── schemas/             # Pydantic 스키마
│   │   ├── consultation.py
│   │   ├── customer.py
│   │   └── plan.py
│   └── services/            # 비즈니스 로직
│       ├── consultation_service.py
│       ├── customer_service.py
│       ├── plan_service.py
│       └── sample_data.py
├── requirements.txt
├── run.py
└── README.md
```

## 샘플 데이터

현재 데이터베이스 없이 샘플 데이터로 동작합니다.

### 사용 가능한 샘플 ID
- 상담 ID: `CONS001`
- 고객 ID: `C001`, `C002`

### 테스트 예시

```bash
# 상담 정보 조회
curl http://localhost:8000/api/consultations/CONS001

# 고객 정보 조회
curl http://localhost:8000/api/customers/C001

# 요금제 검색
curl "http://localhost:8000/api/plans/search?query=5G&filters=family"
```

## 프론트엔드 연동

프론트엔드에서 다음 환경 변수를 설정하세요:

```env
REACT_APP_API_URL=http://localhost:8000
```

또는 프론트엔드 `.env` 파일에 추가:

```
REACT_APP_API_URL=http://localhost:8000
```
