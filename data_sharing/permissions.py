from secrets import compare_digest

from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_async_db
from data_sharing.internal.hashing import get_key_hash
from data_sharing.models import ApiKey
from data_sharing.settings import settings

header_scheme = APIKeyHeader(name="Authorization", scheme_name="Bearer")


def is_authenticated(token=Depends(header_scheme)):
    if not compare_digest(token, settings.DELTA_BEARER_TOKEN):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def is_admin(
    key=Depends(header_scheme), db: AsyncSession = Depends(get_async_db)
):
    key_hash = get_key_hash(key)
    (result,) = (
        await db.execute(select(ApiKey).where(ApiKey.hashed_key == key_hash))
    ).first()
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    role_codes = [r.id for r in result.roles]
    if "ADMIN" not in role_codes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
