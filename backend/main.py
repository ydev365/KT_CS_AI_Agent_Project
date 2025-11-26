from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import auth, chat, stt, history
from db.database import engine
from db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 코드"""
    # 시작 시: 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    yield
    # 종료 시
    print("Shutting down...")


app = FastAPI(
    title="KT CS AI 상담원",
    description="KT 요금제 상담을 위한 AI 에이전트 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(stt.router)
app.include_router(history.router)


@app.get("/")
def root():
    """API 상태 확인"""
    return {
        "status": "running",
        "service": "KT CS AI 상담원",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
