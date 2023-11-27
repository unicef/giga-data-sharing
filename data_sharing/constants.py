import tomllib
from functools import lru_cache

from pydantic import conint
from pydantic_settings import BaseSettings

from data_sharing.settings import settings


class Constants(BaseSettings):
    API_KEY_LENGTH: conint(gt=0) = 64
    BYTES_LENGTH_COMPENSATION: conint(ge=0) = 16
    API_KEY_BYTES_LENGTH: conint(gt=0) = API_KEY_LENGTH - BYTES_LENGTH_COMPENSATION
    ARGON2_NUM_ITERATIONS: conint(gt=0) = 10


@lru_cache
def get_constants():
    return Constants()


@lru_cache
def get_app_version():
    with open(settings.BASE_DIR / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["tool"]["poetry"]["version"]


constants = get_constants()
__version__ = get_app_version()
