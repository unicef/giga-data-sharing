import tomllib
from functools import lru_cache

from pydantic_settings import BaseSettings

from data_sharing.settings import settings


class Constants(BaseSettings):
    pass


@lru_cache
def get_constants():
    return Constants()


@lru_cache
def get_app_version():
    with open(settings.BASE_DIR / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["tool"]["poetry"]["version"]


constants = get_constants()
__version__ = get_app_version()
