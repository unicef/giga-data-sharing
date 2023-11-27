from fastapi import APIRouter, Depends, Security
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_async_db
from data_sharing.models import Role
from data_sharing.permissions import is_authenticated
from data_sharing.schemas.api_key import Role as RoleSchema

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    dependencies=[Security(is_authenticated)],
)


@router.get("", response_model=list[RoleSchema])
async def list_roles(db: AsyncSession = Depends(get_async_db)):
    queryset = await db.execute(select(Role).order_by(Role.id))
    results = queryset.all()
    return [r for (r,) in results]
