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
from data_sharing.models import ApiKey, Role, Schema
from data_sharing.permissions import IsAdmin, IsAuthenticated, auth_scheme
from data_sharing.permissions.utils import extract_sharing_key_components, get_current_user
from data_sharing.schemas.api_key import (
    CreateApiKeyRequest,
    SafeApiKey,
    UpdateApiKeyRequest,
)
from data_sharing.schemas.delta_sharing import ProfileFile
from data_sharing.settings import settings

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
    body: CreateApiKeyRequest, 
    db: AsyncSession = Depends(get_async_db),
    current_user: ApiKey = Depends(get_current_user)
):
    # Double-check: Verify the requesting user is an admin
    role_codes = [r.id for r in current_user.roles]
    if "ADMIN" not in role_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create API keys"
        )
    
    # Check if ADMIN role is requested
    is_admin = "ADMIN" in body.roles if body.roles else False
    
    # If not admin, schemas are required
    if not is_admin and not body.schemas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schemas are required for non-admin API keys",
        )
    
    # If admin, no schemas needed
    if is_admin:
        schemas = []
    else:
        schemas_result = await db.execute(select(Schema).where(Schema.id.in_(body.schemas)))
        schemas = schemas_result.scalars().all()
        schema_ids = {schema.id for schema in schemas}
        if len(diff := set(body.schemas).difference(schema_ids)) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid schema(s): {', '.join([f'`{d}`' for d in diff])}",
            )
    
    new_key = token_urlsafe(constants.API_KEY_BYTES_LENGTH)
    now = datetime.now().astimezone(ZoneInfo("UTC"))
    api_key = ApiKey(
        description=body.description,
        secret=get_key_hash(new_key),
        expiration=now + timedelta(days=body.validity) if body.validity > 0 else None,
    )
    
    # Handle roles
    if body.roles:
        roles_result = await db.execute(select(Role).where(Role.id.in_(body.roles)))
        roles = roles_result.scalars().all()
        role_ids = {role.id for role in roles}
        if len(diff := set(body.roles).difference(role_ids)) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role(s): {', '.join([f'`{d}`' for d in diff])}",
            )
        api_key.roles.update(roles)
    
    # Handle schemas
    api_key.schemas.update(schemas)
    db.add(api_key)
    await db.commit()
    return dict(
        bearerToken=f"{api_key.id}:{new_key}", expirationTime=api_key.expiration
    )


@router.patch(
    "/{api_key_id}",
    response_model=SafeApiKey,
    dependencies=[Security(IsAdmin.raises(True))],
)
async def update_api_key(
    api_key_id: UUID4,
    body: UpdateApiKeyRequest,
    db: AsyncSession = Depends(get_async_db),
):
    api_key = await db.scalar(select(ApiKey).where(ApiKey.id == str(api_key_id)))
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    role_codes = [r.id for r in api_key.roles]
    is_admin = "ADMIN" in role_codes
    
    # Update schemas if provided
    if body.schemas is not None:
        if not is_admin and not body.schemas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Schemas are required for non-admin API keys",
            )
        
        if is_admin:
            api_key.schemas.clear()
        else:
            schemas_result = await db.execute(select(Schema).where(Schema.id.in_(body.schemas)))
            schemas = schemas_result.scalars().all()
            schema_ids = {schema.id for schema in schemas}
            if len(diff := set(body.schemas).difference(schema_ids)) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid schema(s): {', '.join([f'`{d}`' for d in diff])}",
                )
            api_key.schemas.clear()
            api_key.schemas.update(schemas)
    
    # Update roles if provided
    if body.roles is not None:
        if "ADMIN" in body.roles:
            # Admin role requested - only allow if no schemas assigned
            admin_role = await db.scalar(select(Role).where(Role.id == "ADMIN"))
            if admin_role:
                api_key.roles.clear()
                api_key.roles.add(admin_role)
                api_key.schemas.clear()
        else:
            roles_result = await db.execute(select(Role).where(Role.id.in_(body.roles)))
            roles = roles_result.scalars().all()
            role_ids = {role.id for role in roles}
            if len(diff := set(body.roles).difference(role_ids)) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role(s): {', '.join([f'`{d}`' for d in diff])}",
                )
            api_key.roles.clear()
            api_key.roles.update(roles)
    
    await db.commit()
    await db.refresh(api_key)
    return api_key


@router.delete(
    "/{api_key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
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
