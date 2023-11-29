from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from data_sharing.db import get_async_db
from data_sharing.models import ApiKey

from .scheme import auth_scheme


def extract_sharing_key_components(
    key: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
) -> tuple[str, str]:
    split = key.credentials.split(":")
    if len(split) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized or malformed sharing key",
        )

    return split[0], split[1]


async def get_current_user(
    key=Depends(extract_sharing_key_components),
    db: AsyncSession = Depends(get_async_db),
) -> ApiKey:
    id_, secret = key
    result = await db.scalar(select(ApiKey).where(ApiKey.id == id_))
    return result
