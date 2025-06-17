from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_async_db
from data_sharing.internal.hashing import verify_key
from data_sharing.models import ApiKey

from .base import BasePermission
from .utils import extract_sharing_key_components, get_current_user

# Role to Schema Mapping
ROLE_TO_SCHEMA = {
    "SCHM": "school-master",
    "QOS": "qos",
    "REF": "school-reference",
    "GERR": "school-geolocation-error",
}


# Extract known schema and country codes from role list
def parse_user_roles(roles: list[str]):
    known_schemas = set(ROLE_TO_SCHEMA.keys())
    schema_roles = {ROLE_TO_SCHEMA[r] for r in roles if r in known_schemas}
    country_roles = {r for r in roles if r not in known_schemas and r != "ADMIN"}
    return schema_roles, country_roles


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
            print(f"[DEBUG] API key not found: {key_id}")
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        if result.expiration and result.expiration < now:
            print(f"[DEBUG] API key expired: {key_id}")
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        if not verify_key(secret, result.secret):
            print(f"[DEBUG] API key secret mismatch: {key_id}")
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        print(
            f"[DEBUG] Authenticated API key: {key_id} with roles {[r.id for r in result.roles]}"
        )
        return True


class IsAdmin(BasePermission):
    async def __call__(
        self,
        key=Depends(extract_sharing_key_components),
        db: AsyncSession = Depends(get_async_db),
    ):
        key_id, secret = key
        result = await db.scalar(select(ApiKey).where(ApiKey.id == key_id))
        if result is None or not verify_key(secret, result.secret):
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return False

        role_codes = [r.id for r in result.roles]
        if "ADMIN" not in role_codes:
            if self.raise_exceptions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            return False

        return True


class HasTablePermissions(BasePermission):
    def __call__(
        self,
        schema_name: str = Path(...),
        table_name: str = Path(...),
        current_user: ApiKey = Depends(get_current_user),
    ):
        from data_sharing.permissions.access_control import user_has_access_to_table

        if user_has_access_to_table(current_user, schema_name, table_name):
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this table"
        )
