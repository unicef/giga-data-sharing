from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_db
from data_sharing.models import ApiKey as ApiKeyModel
from data_sharing.permissions import is_authenticated
from data_sharing.schemas.api_key import ApiKey, CreateApiKeyRequest

router = APIRouter(
    prefix="/api-keys",
    tags=["api_key"],
    dependencies=[Security(is_authenticated)],
)


@router.get("", response_model=list[ApiKey])
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    queryset = await db.execute(select("*").select_from(ApiKeyModel))
    return queryset


@router.get("/{api_key_id}", response_model=ApiKey)
async def view_api_key_details():
    raise NotImplementedError


@router.post("", response_model=ApiKey)
async def generate_api_key(body: CreateApiKeyRequest):
    raise NotImplementedError


@router.delete("/{api_key_id}", response_model=ApiKey)
async def revoke_api_key(api_key_id: UUID4):
    raise NotImplementedError
