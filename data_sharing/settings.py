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
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_DATABASE: str
    DB_HOST: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRESQL_USERNAME}:{self.POSTGRESQL_PASSWORD}@{self.DB_HOST}:5432/{self.POSTGRESQL_DATABASE}"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
