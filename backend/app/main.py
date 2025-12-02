from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from .routers import consultations, customers, plans, auth, voice, chat, summary
from .websocket_manager import sio

# FastAPI 앱 생성
app = FastAPI(
    title="KT CS AI Agent API",
    description="KT 고객센터 AI 상담 지원 시스템 백엔드 API",
    version="2.0.0"
)

# CORS 설정 - 프론트엔드 연동을 위해
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기존 라우터
app.include_router(consultations.router)
app.include_router(customers.router)
app.include_router(plans.router)

# 신규 라우터
app.include_router(auth.router)
app.include_router(voice.router)
app.include_router(chat.router)
app.include_router(summary.router)


@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "KT CS AI Agent API",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "고객 인증 (POST /api/auth/verify)",
            "AI 상담 (POST /api/chat/session, /api/chat/message)",
            "음성 처리 (POST /api/voice/stt, /api/voice/tts)",
            "요약 및 추천 (GET /api/summary/{session_id})"
        ]
    }


@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    from .core.redis_client import redis_client

    redis_status = "connected" if redis_client.ping() else "disconnected"

    return {
        "status": "healthy",
        "redis": redis_status
    }


# Socket.IO ASGI 앱과 FastAPI 앱 결합
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
