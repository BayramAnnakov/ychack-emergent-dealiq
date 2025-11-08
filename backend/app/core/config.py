"""
Configuration settings for DealIQ application
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "DealIQ"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "DealIQ - AI-Powered CRM Intelligence"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # Database
    DATABASE_URL: Optional[str] = "postgresql://dealiq:dealiq@localhost/dealiq"
    REDIS_URL: Optional[str] = "redis://localhost:6379"

    # Claude API
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "data/uploads"
    ALLOWED_EXTENSIONS: set = {".csv", ".xlsx", ".xls", ".json"}

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Agent Settings
    AGENT_TIMEOUT: int = 120  # seconds
    MAX_CONTEXT_LENGTH: int = 100000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()