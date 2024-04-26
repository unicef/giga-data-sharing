from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import UUID4
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"

    PYTHON_ENV: Literal["local", "development", "staging", "production"] = "production"
    DEPLOY_ENV: Literal["local", "dev", "stg", "prd"] = "local"
    BASE_DIR: Path = Path(__file__).parent.parent
    SECRET_KEY: str
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]
    DELTA_BEARER_TOKEN: str
    STORAGE_ACCESS_KEY: str
    STORAGE_ACCOUNT_NAME: str
    CONTAINER_NAME: str
    CONTAINER_PATH: str
    DELTA_SHARING_HOST: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_DATABASE: str
    DB_HOST: str
    INGRESS_HOST: str
    ADMIN_API_KEY: UUID4
    SENTRY_DSN: str = ""
    COMMIT_SHA: str = ""

    @property
    def IN_PRODUCTION(self) -> bool:
        return self.PYTHON_ENV != "local"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRESQL_USERNAME}:{self.POSTGRESQL_PASSWORD}@{self.DB_HOST}:5432/{self.POSTGRESQL_DATABASE}"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRESQL_USERNAME}:{self.POSTGRESQL_PASSWORD}@{self.DB_HOST}:5432/{self.POSTGRESQL_DATABASE}"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
