from typing import Union
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Shared settings across all environments"""

    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"

    # Database Configs
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_PRE_PING: bool = True
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_QUERY_CACHE_SIZE: int = 0

    # Email Configs
    RESEND_FROM_EMAIL: str
    RESEND_FROM_NAME: str
    RESEND_API_KEY: str

    # JWT Configs
    JWT_ALGORITHM: str

    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    JWT_ACCESS_EXPIRE_MINUTES: int
    JWT_REFRESH_EXPIRE_MINUTES: int

    MAX_ACTIVE_SESSIONS: int = 5

    # Verification Token Configs
    VERIFICATION_TOKEN_SECRET: str
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 1440  # 24 hours

    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


class DevelopmentSettings(AppSettings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


class ProductionSettings(AppSettings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str]  # Must be explicitly set


class TestSettings(AppSettings):
    DATABASE_URL: str

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Union[DevelopmentSettings, ProductionSettings, TestSettings]:
    env = os.getenv("ENVIRONMENT", "development").lower()
    config_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "test": TestSettings,
    }
    if env not in config_map:
        env = "development"
    return config_map[env]()


settings = get_settings()
