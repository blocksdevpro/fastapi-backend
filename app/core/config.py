from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    JWT_ALGORITHM: str

    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    JWT_ACCESS_EXPIRE_MINUTES: int
    JWT_REFRESH_EXPIRE_MINUTES: int

    MAX_ACTIVE_SESSIONS: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()  # type: ignore[call-arg]
