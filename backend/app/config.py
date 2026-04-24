from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    JWT_SECRET: str="replace_with_a_long_random_secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    # BACKEND_CORS_ORIGINS: str = "http://localhost:3001"
    # BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3001","http://192.168.71.1:3001","http://192.168.48.1:3001"]
    BACKEND_CORS_ORIGINS: List[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
