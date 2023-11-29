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
from data_sharing.permissions import IsAdmin, IsAuthenticated, auth_scheme
from data_sharing.permissions.utils import extract_sharing_key_components
from data_sharing.schemas.api_key import CreateApiKeyRequest, SafeApiKey
from data_sharing.schemas.delta_sharing import ProfileFile

router = APIRouter(
    prefix="/api-keys",
    tags=["api_key"],
    dependencies=[Security(IsAuthenticated.raises(True))],
)


@router.get(
    "", response_model=list[SafeApiKey], dependencies=[Security(IsAdmin.raises(True))]
)
async def list_api_keys(db: AsyncSession = Depends(get_async_db)):
    return await db.scalars(select(ApiKey).order_by(ApiKey.created.desc()))


@router.get("/me", response_model=SafeApiKey)
async def view_api_key_details_for_current_user(
    key=Depends(auth_scheme), db: AsyncSession = Depends(get_async_db)
):
    key_id, key_secret = extract_sharing_key_components(key)
    queryset = await db.scalar(select(ApiKey).where(ApiKey.id == key_id))
    if queryset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return queryset


@router.get(
    "/{api_key_id}",
    response_model=SafeApiKey,
    dependencies=[Security(IsAdmin.raises(True))],
)
async def view_api_key_details(
    api_key_id: UUID4, db: AsyncSession = Depends(get_async_db)
):
    queryset = await db.scalar(select(ApiKey).where(ApiKey.id == str(api_key_id)))
    if queryset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return queryset


@router.post(
    "",
    response_model=ProfileFile,
    response_description=(
        "On successful key generation, the Delta Sharing Protocol Profile File is"
        " returned, which contains the API key. Save this in a secure location as it"
        " will not be shown again."
    ),
    dependencies=[Security(IsAdmin.raises(True))],
)
async def generate_api_key(
    body: CreateApiKeyRequest, db: AsyncSession = Depends(get_async_db)
):
    new_key = token_urlsafe(constants.API_KEY_BYTES_LENGTH)
    now = datetime.now().astimezone(ZoneInfo("UTC"))
    api_key = ApiKey(
        description=body.description,
        secret=get_key_hash(new_key),
        expiration=now + timedelta(days=body.validity) if body.validity > 0 else None,
    )
    roles = await db.scalars(select(Role).where(Role.id.in_(body.roles)))
    api_key.roles.update(roles)
    db.add(api_key)
    await db.commit()
    return dict(
        bearerToken=f"{api_key.id}:{new_key}", expirationTime=api_key.expiration
    )


@router.delete(
    "/{api_key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    dependencies=[Security(IsAdmin.raises(True))],
)
async def revoke_api_key(api_key_id: UUID4, db: AsyncSession = Depends(get_async_db)):
    await db.execute(delete(ApiKey).where(ApiKey.id == str(api_key_id)))
    await db.commit()
