from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"

    BASE_DIR: Path = Path(__file__).parent.parent
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]
    DELTA_BEARER_TOKEN: str
    STORAGE_ACCESS_KEY: str
    DELTA_SHARING_HOST: str
    PYTHON_ENV: str = "production"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
