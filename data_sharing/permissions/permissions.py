from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_async_db
from data_sharing.internal.hashing import verify_key
from data_sharing.models import ApiKey

from .base import BasePermission
from .utils import extract_sharing_key_components


class IsAuthenticated(BasePermission):
    async def __call__(
        self,
        key=Depends(extract_sharing_key_components),
        db: AsyncSession = Depends(get_async_db),
    ):
        key_id, secret = key
        now = datetime.now().astimezone(ZoneInfo("UTC"))
        result = await db.scalar(select(ApiKey).where(ApiKey.id == key_id))
        if result is None:
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        if (
            result.expiration is not None and result.expiration < now
        ) or not verify_key(secret, result.secret):
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        return True


class IsAdmin(BasePermission):
    async def __call__(
        self,
        key=Depends(extract_sharing_key_components),
        db: AsyncSession = Depends(get_async_db),
    ):
        key_id, secret = key
        result = await db.scalar(select(ApiKey).where(ApiKey.id == key_id))
        if result is None:
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        role_codes = [r.id for r in result.roles]
        if "ADMIN" not in role_codes:
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            return False

        return True
