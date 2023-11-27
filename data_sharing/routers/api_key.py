from datetime import datetime, timedelta
from secrets import token_urlsafe
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import UUID4
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.constants import constants
from data_sharing.db import get_async_db
from data_sharing.internal.hashing import get_key_hash
from data_sharing.models import ApiKey, Role
from data_sharing.permissions import is_authenticated
from data_sharing.schemas.api_key import CreateApiKeyRequest, SafeApiKey
from data_sharing.schemas.delta_sharing import ProfileFile

router = APIRouter(
    prefix="/api-keys",
    tags=["api_key"],
    dependencies=[Security(is_authenticated)],
)


@router.get("", response_model=list[SafeApiKey])
async def list_api_keys(db: AsyncSession = Depends(get_async_db)):
    queryset = await db.execute(select(ApiKey).order_by(ApiKey.created.desc()))
    results = queryset.all()
    return [r for (r,) in results]


@router.get("/{api_key_id}", response_model=SafeApiKey)
async def view_api_key_details(
    api_key_id: UUID4, db: AsyncSession = Depends(get_async_db)
):
    queryset = await db.execute(select(ApiKey).where(ApiKey.id == str(api_key_id)))
    (result,) = queryset.first()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return result


@router.post("", response_model=ProfileFile)
async def generate_api_key(
    body: CreateApiKeyRequest, db: AsyncSession = Depends(get_async_db)
):
    new_key = token_urlsafe(constants.API_KEY_BYTES_LENGTH)
    now = datetime.now().astimezone(ZoneInfo("UTC"))
    api_key = ApiKey(
        description=body.description,
        key=new_key[: constants.API_KEY_HINT_LENGTH],
        hashed_key=get_key_hash(new_key),
        expiration=now + timedelta(days=body.validity) if body.validity > 0 else None,
    )
    roles_queryset = await db.execute(select(Role).where(Role.id.in_(body.roles)))
    roles = [r for (r,) in roles_queryset.all()]
    api_key.roles.update(roles)
    db.add(api_key)
    await db.commit()
    return dict(bearerToken=new_key, expirationTime=api_key.expiration)


@router.delete(
    "/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def revoke_api_key(api_key_id: UUID4, db: AsyncSession = Depends(get_async_db)):
    await db.execute(delete(ApiKey).where(ApiKey.id == str(api_key_id)))
