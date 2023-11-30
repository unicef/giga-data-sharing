from fastapi import APIRouter, Depends, Security
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_sharing.db import get_async_db
from data_sharing.models import Role
from data_sharing.permissions import IsAdmin
from data_sharing.schemas.api_key import Role as RoleSchema

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    dependencies=[Security(IsAdmin.raises(True))],
)


@router.get("", response_model=list[RoleSchema])
async def list_roles(db: AsyncSession = Depends(get_async_db)):
    return await db.scalars(select(Role).order_by(Role.id))
