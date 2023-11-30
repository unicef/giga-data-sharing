from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from pydantic import UUID4
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

apikey_role_association_table = sa.Table(
    "apikey_role_association_table",
    BaseModel.metadata,
    sa.Column(
        "api_key_id", sa.ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False
    ),
    sa.Column("role_id", sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
)


class Role(BaseModel):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(sa.VARCHAR(5), primary_key=True, index=True)
    description: Mapped[str] = mapped_column(nullable=False)


class ApiKey(BaseModel):
    __tablename__ = "api_keys"

    id: Mapped[UUID4] = mapped_column(primary_key=True, index=True, default=uuid4)
    created: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=func.now()
    )
    description: Mapped[str] = mapped_column()
    secret: Mapped[str] = mapped_column(nullable=False, index=True)
    expiration: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), index=True, nullable=True
    )
    roles: Mapped[set[Role]] = relationship(
        secondary=apikey_role_association_table,
        lazy="selectin",
        cascade="all, delete",
    )
