from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_async_db
from data_sharing.internal.hashing import verify_key
from data_sharing.models import ApiKey

from .base import BasePermission
from .utils import extract_sharing_key_components, get_current_user


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


class HasSchemaPermissions(BasePermission):
    async def __call__(
        self, 
        current_user: ApiKey = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
    ):
        """Check if user can access any schema or is admin"""
        role_codes = [r.id for r in current_user.roles]
        if "ADMIN" in role_codes:
            return True
        
        # If no schemas assigned, no access
        if not current_user.schemas:
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            return False
        
        return True


class HasTablePermissions(BasePermission):
    async def __call__(
        self, 
        schema_name: str = Path(),
        table_name: str = Path(), 
        current_user: ApiKey = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
    ):
        role_codes = [r.id for r in current_user.roles]
        if "ADMIN" in role_codes:
            return True

        # Check schema access first
        schema_ids = [s.id for s in current_user.schemas]
        if schema_name not in schema_ids:
            if self.raise_exceptions:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Schema '{schema_name}' not found or access denied"
                )
            return False
        
        # Check table (country) access if roles are specified
        if table_name and current_user.roles and "ADMIN" not in role_codes:
            if table_name not in role_codes:
                if self.raise_exceptions:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Table '{table_name}' not found or access denied"
                    )
                return False
        
        return True
