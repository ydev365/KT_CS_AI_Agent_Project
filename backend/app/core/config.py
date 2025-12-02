from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # OpenAI API 설정
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    WHISPER_MODEL: str = "whisper-1"
    TTS_MODEL: str = "tts-1"
    TTS_VOICE: str = "nova"  # alloy, echo, fable, onyx, nova, shimmer
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # 세션 설정
    SESSION_TIMEOUT_MINUTES: int = 30

    # Vector DB 설정 (ChromaDB)
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "kt_plans"

    # 데이터 경로
    PLANS_CSV_PATH: str = "./data/plans.csv"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
