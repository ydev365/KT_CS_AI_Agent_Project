# KT CS AI 상담원

KT 요금제 상담을 위한 AI 에이전트 시스템

## 기술 스택

- **Backend**: FastAPI (Python)
- **Frontend**: React
- **Database**: MySQL
- **Vector DB**: ChromaDB
- **LLM**: OpenAI GPT-4
- **STT**: OpenAI Whisper
- **웹크롤링**: Firecrawl API

## 프로젝트 구조

```
├── backend/
│   ├── main.py              # FastAPI 앱
│   ├── config.py            # 설정
│   ├── api/routes/          # API 엔드포인트
│   ├── services/            # 비즈니스 로직
│   ├── db/                  # DB 모델 및 연결
│   ├── vectordb/            # ChromaDB, Firecrawl
│   └── schemas/             # Pydantic 모델
├── frontend/
│   └── src/
│       ├── components/      # React 컴포넌트
│       ├── services/        # API 호출
│       └── styles/          # CSS
└── data/
    └── chroma/              # VectorDB 저장소
```

## 설치 및 실행

### 1. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 API 키와 DB 정보를 입력:

```env
OPENAI_API_KEY=your_openai_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=kt_cs_db
CHROMA_PERSIST_DIR=./data/chroma
```

### 2. MySQL 데이터베이스 생성

```sql
CREATE DATABASE kt_cs_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Backend 실행

```bash
cd backend

# 가상환경 생성 및 활성화
py -3.11 -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

Backend: http://localhost:8000

### 4. 요금제 데이터 크롤링 (최초 1회)<= 이것은 내가 이미 크롤링을 해서 chromadb에 저장되어있으므로 안해도 된다.

```bash
cd backend
venv\Scripts\activate
python -m vectordb.firecrawl_loader
```

### 5. 샘플 데이터 생성 (더미데이터로 미리 KT 회원인사람들 등록되어있게 하는거)

```bash
cd backend
venv\Scripts\activate
python -m db.init_db
```


### 6. Frontend 실행

```bash
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm start
```

Frontend: http://localhost:3000

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/verify` | 전화번호로 고객 인증 |
| POST | `/api/chat/message` | 채팅 메시지 전송 |
| POST | `/api/chat/end` | 상담 종료 (요약 생성) |
| POST | `/api/stt/transcribe` | 음성→텍스트 변환 |
| GET | `/api/history/{phone}` | 상담 이력 조회 |
| GET | `/api/history/session/{id}` | 세션 상세 조회 |

## 주요 기능

1. **고객 인증**: 전화번호 입력으로 KT 회원 여부 확인
2. **AI 상담**: RAG 기반 요금제 상담 (GPT-4 + ChromaDB)
3. **음성 입력**: Whisper API로 음성→텍스트 변환
4. **맞춤 추천**: 고객 나이, 현재 요금제 기반 추천
5. **상담원 연결**: "상담원 연결" 발화 시 안내
6. **상담 요약**: 대화 종료 시 자동 요약 저장
7. **이력 조회**: 이전 상담 내역 확인

## 크롤링 대상 요금제 (12개)

- 요고 다이렉트
- 5G 초이스
- 5G 스페셜/베이직
- 5G 심플
- 5G 슬림
- 5G 슬림(이월)
- 5G Y (만 34세 이하)
- 5G Y틴 (만 18세 이하)
- 5G 주니어 (만 12세 이하)
- 5G 시니어 (만 65세 이상)
- 5G 웰컴 (외국인 전용)
- 5G 복지 (장애인 전용)


### sample customer data 
김철수 010-1234-5678
이영희 010-8765-4321
박지민 010-1111-2222
최민수 010-5555-6666
정미영 010-9999-8888


트러블슈팅 파트

📂 [트러블슈팅 로그] MySQL 9.x와 Python 연동 시 'Access Denied' 문제 해결
1. 문제 상황 (Issue)
환경: Python 3.11 (FastAPI, SQLAlchemy), MySQL 9.4.0 (Docker/Local)

현상: .env 파일에 정확한 비밀번호를 입력했음에도 불구하고, 애플리케이션 구동 시 DB 연결 실패 오류 발생.

에러 메시지:

Python

sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1045, "Access denied for user 'root'@'localhost' (using password: YES)")
2. 원인 분석 (Root Cause Analysis)
단순한 비밀번호 오입력이 아닌, MySQL의 인증 프로토콜과 애플리케이션의 접속 방식 간의 불일치가 원인이었음.

MySQL root 계정의 보안 정책 (Socket vs TCP/IP):

MySQL의 root@localhost 계정은 보안상 외부 네트워크(TCP/IP) 접속보다는 **로컬 소켓 파일(Unix Socket)**을 통한 접속을 기본으로 선호하거나 강제하는 경우가 많음.

특히 최신 버전(MySQL 8.0/9.x)에서는 root 계정에 대해 외부 접속 권한이 엄격하게 제한됨.

클라이언트(Python)의 접속 시도:

Python의 SQLAlchemy 및 PyMySQL 드라이버는 기본적으로 **TCP/IP 프로토콜(Host: localhost, Port: 3306)**을 사용하여 접속을 시도함.

충돌 발생:

서버(MySQL)는 **"로컬 파일(Socket)로 와라"**라고 기다리고 있는데, 클라이언트(Python)는 **"네트워크 포트(TCP)로 들어가겠다"**고 요청하니, 비밀번호가 맞아도 접속 방식이 맞지 않아 Access denied 처리됨.

3. 해결 과정 (Solution)
root 계정의 설정을 억지로 변경하여 보안을 낮추는 대신, **애플리케이션 전용 사용자(Dedicated User)**를 생성하여 TCP/IP 접속을 명시적으로 허용하는 방식을 채택함.

Step 1: MySQL 9.x 표준에 맞는 전용 사용자 생성 root 대신 외부 접속(%)이 허용된 kt_user를 생성함. 호스트를 %로 지정하여 localhost 및 127.0.0.1을 포함한 모든 TCP/IP 접속을 수용하도록 설정.

SQL

-- 관리자(root) 권한으로 실행
CREATE USER 'kt_user'@'%' IDENTIFIED BY '3751'; -- MySQL 9.x 기본 인증(SHA2) 사용
GRANT ALL PRIVILEGES ON kt_cs_db.* TO 'kt_user'@'%';
FLUSH PRIVILEGES;
Step 2: 환경 변수(.env) 업데이트 애플리케이션이 root가 아닌 새로 생성한 계정을 사용하도록 변경.

Ini, TOML

# .env
MYSQL_USER=kt_user
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_DATABASE=kt_cs_db
4. 결과 및 배운 점 (Outcome & Key Takeaways)
결과: 서버 재시작 후 OperationalError 1045가 즉시 해결되었으며, FastAPI 서버와 MySQL 9.4가 정상적으로 연동됨.

기술적 성과:

MySQL의 Socket 접속과 TCP/IP 접속의 차이를 명확히 이해함.

데이터베이스 운영 시, 보안과 확장성을 위해 root 계정 사용을 지양하고 **서비스 전용 계정(Service Account)**을 사용하는 Best Practice를 적용함.

MySQL 9.x 버전의 인증 방식 변화(mysql_native_password 삭제)에 따른 최신 환경 대응 능력을 기름.
