from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    BCRYPT_ROUNDS: int
    JWT_ALGORITHM: str

    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    JWT_ACCESS_EXPIRE_MINUTES: int
    JWT_REFRESH_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
