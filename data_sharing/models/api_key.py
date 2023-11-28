from uuid import uuid4

import sqlalchemy as sa
from pydantic import UUID4, AwareDatetime, constr
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

    id: Mapped[constr(min_length=3, max_length=5)] = mapped_column(
        sa.VARCHAR(5), primary_key=True, index=True
    )
    description: Mapped[str] = mapped_column(nullable=False)


class ApiKey(BaseModel):
    __tablename__ = "api_keys"

    id: Mapped[UUID4] = mapped_column(primary_key=True, index=True, default=uuid4)
    created: Mapped[AwareDatetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=func.now()
    )
    description: Mapped[str] = mapped_column()
    key: Mapped[constr(max_length=6)] = mapped_column(sa.VARCHAR(6), nullable=False)
    hashed_key: Mapped[constr(min_length=1)] = mapped_column(
        sa.String, nullable=False, index=True
    )
    expiration: Mapped[AwareDatetime] = mapped_column(
        sa.DateTime(timezone=True), index=True
    )
    roles: Mapped[set[Role]] = relationship(
        secondary=apikey_role_association_table,
        lazy="selectin",
        cascade="all, delete",
    )
