import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Clinical Post-Discharge Monitoring System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./app.db"

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    OPENROUTER_API_KEY: Optional[str] = "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"
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    AI_TEXT_MODEL: str = "openrouter/free"
    AI_VISION_MODEL: str = "inclusionai/ling-3.0-flash-vl:free"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
