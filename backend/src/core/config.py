"""
AppConfig - Singleton Pattern
Centralized configuration management
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import BaseModel, ConfigDict
class Settings(BaseSettings):
    # App
    APP_NAME: str = "Expense Tracker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase
    SUPABASE_URL: str = "https://etfnkdvsktxljlcuqtey.supabase.co"
    SUPABASE_KEY: str = "test-anon-key"
    SUPABASE_SERVICE_KEY: str = "test-service-key"

    # JWT
    JWT_SECRET: str = "default-jwt-secret-key-expense-tracker-ipz42"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    model_config = ConfigDict(env_file=".env", case_sensitive=True)


# SINGLETON via lru_cache
@lru_cache()
def get_settings() -> Settings:
    """Returns singleton Settings instance"""
    return Settings()


# Global instance
settings = get_settings()
