from datetime import datetime
from secrets import compare_digest
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_async_db
from data_sharing.internal.hashing import verify_key
from data_sharing.models import ApiKey
from data_sharing.settings import settings

from .base import BasePermission
from .scheme import header_scheme
from .utils import extract_sharing_key_components


class IsAuthenticated(BasePermission):
    async def __call__(
        self, key=Depends(header_scheme), db: AsyncSession = Depends(get_async_db)
    ):
        key_id, secret = extract_sharing_key_components(key)
        if compare_digest(settings.DELTA_BEARER_TOKEN, secret):
            return True

        now = datetime.now().astimezone(ZoneInfo("UTC"))
        results = (await db.execute(select(ApiKey).where(ApiKey.id == key_id))).first()
        if results is None:
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        (result,) = results
        if result.expiration < now or not verify_key(secret, result.secret):
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        return True


class IsAdmin(BasePermission):
    async def __call__(
        self,
        key=Depends(header_scheme),
        db: AsyncSession = Depends(get_async_db),
        is_authenticated=Depends(IsAuthenticated.raises(False)),
    ):
        key_id, secret = extract_sharing_key_components(key)
        results = (await db.execute(select(ApiKey).where(ApiKey.id == key_id))).first()
        if results is None:
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        (result,) = results
        role_codes = [r.id for r in result.roles]
        if "ADMIN" not in role_codes:
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            return False

        return True
