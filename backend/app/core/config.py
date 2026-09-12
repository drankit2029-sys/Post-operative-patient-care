import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Clinical Post-Discharge Monitoring System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./app.db"

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "[http://127.0.0.1:5173](http://127.0.0.1:5173)",
        "http://localhost:5174",
        "[http://127.0.0.1:5174](http://127.0.0.1:5174)",
        "http://localhost:3000",
        "[http://127.0.0.1:3000](http://127.0.0.1:3000)",
    ]

    # Mistral AI Configuration
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_BASE_URL: str = "https://api.mistral.ai/v1"

    # Models
    AI_TEXT_MODEL: str = "mistral-small-latest"
    AI_VISION_MODEL: str = "pixtral-12b-2409"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
