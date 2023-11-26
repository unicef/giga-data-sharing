import sqlalchemy as sa
from pydantic import UUID4, AwareDatetime, constr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

apikey_country_association_table = sa.Table(
    "apikey_country_association_table",
    BaseModel.metadata,
    sa.Column("api_key_id", sa.ForeignKey("api_keys.id"), nullable=False),
    sa.Column("country_id", sa.ForeignKey("countries.id"), nullable=False),
)


class Country(BaseModel):
    __tablename__ = "countries"

    id: Mapped[UUID4] = mapped_column(primary_key=True, index=True)
    iso_3166_alpha_3: Mapped[constr(min_length=3, max_length=3)] = mapped_column(
        sa.VARCHAR(3),
        nullable=False,
        index=True,
        unique=True,
    )
    name: Mapped[str] = mapped_column(nullable=False)


class ApiKey(BaseModel):
    __tablename__ = "api_keys"

    id: Mapped[UUID4] = mapped_column(primary_key=True, index=True)
    key: Mapped[constr(min_length=64, max_length=64)] = mapped_column(
        sa.VARCHAR(64), nullable=False
    )
    expiration: Mapped[AwareDatetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(nullable=False, default=False)
    permissions: Mapped[list[Country]] = relationship(
        secondary=apikey_country_association_table
    )
