from datetime import datetime, timedelta
from secrets import token_urlsafe
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import UUID4, BaseModel
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
from data_sharing.settings import settings

router = APIRouter(
    prefix="/api-keys",
    tags=["api_key"],
    dependencies=[Security(IsAuthenticated.raises(True))],
)


class UpdateApiKeyRolesRequest(BaseModel):
    roles: list[str]


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
        "On successful key generation, the Delta Sharing Protocol Profile File is "
        "returned. Save this in a secure location as it will not be shown again."
    ),
    dependencies=[Security(IsAdmin.raises(True))],
)
async def generate_api_key(
    body: CreateApiKeyRequest, db: AsyncSession = Depends(get_async_db)
):
    # Validate role IDs exist
    role_query = await db.execute(select(Role).where(Role.id.in_(body.roles)))
    roles = role_query.scalars().all()
    valid_role_ids = {role.id for role in roles}
    invalid_roles = set(body.roles) - valid_role_ids
    if invalid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid roles: {', '.join(sorted(invalid_roles))}",
        )

    now = datetime.now().astimezone(ZoneInfo("UTC"))
    new_secret = token_urlsafe(constants.API_KEY_BYTES_LENGTH)
    new_api_key = ApiKey(
        description=body.description,
        secret=get_key_hash(new_secret),
        expiration=(now + timedelta(days=body.validity)) if body.validity > 0 else None,
    )
    new_api_key.roles.update(roles)
    db.add(new_api_key)
    await db.commit()

    return {
        "bearerToken": f"{new_api_key.id}:{new_secret}",
        "expirationTime": new_api_key.expiration,
    }


@router.patch("/{api_key_id}/roles", dependencies=[Security(IsAdmin.raises(True))])
async def update_api_key_roles(
    api_key_id: UUID4,
    body: UpdateApiKeyRolesRequest,
    db: AsyncSession = Depends(get_async_db),
):
    api_key = await db.scalar(select(ApiKey).where(ApiKey.id == str(api_key_id)))
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    role_query = await db.execute(select(Role).where(Role.id.in_(body.roles)))
    roles = role_query.scalars().all()
    valid_role_ids = {r.id for r in roles}
    invalid_roles = set(body.roles) - valid_role_ids
    if invalid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid roles: {', '.join(sorted(invalid_roles))}",
        )

    api_key.roles.clear()
    api_key.roles.update(roles)
    await db.commit()

    return {"detail": "Roles updated successfully"}


@router.delete(
    "/{api_key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(IsAdmin.raises(True))],
)
async def revoke_api_key(api_key_id: UUID4, db: AsyncSession = Depends(get_async_db)):
    if api_key_id == settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete the admin token",
        )
    await db.execute(delete(ApiKey).where(ApiKey.id == str(api_key_id)))
    await db.commit()
