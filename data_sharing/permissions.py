from datetime import datetime
from secrets import compare_digest
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_async_db
from data_sharing.internal.hashing import get_key_hash, verify_key
from data_sharing.models import ApiKey
from data_sharing.settings import settings

header_scheme = APIKeyHeader(name="X-Giga-Sharing-Key")


async def is_authenticated(
    key=Depends(header_scheme), db: AsyncSession = Depends(get_async_db)
):
    if compare_digest(key, settings.DELTA_BEARER_TOKEN):
        return True

    now = datetime.now().astimezone(ZoneInfo("UTC"))
    results = (await db.execute(select(ApiKey).where(ApiKey.expiration > now))).all()
    results = [r for (r,) in results]
    for r in results:
        if verify_key(key, r.hashed_key):
            return True

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
