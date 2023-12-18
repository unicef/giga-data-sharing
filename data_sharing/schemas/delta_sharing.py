from datetime import datetime
from typing import Generic, TypeVar

from pydantic import UUID4, AnyHttpUrl, BaseModel, Field, conint

from data_sharing.annotations.delta_sharing import (
    ProfileFileDescriptions,
    table_version_description,
)
from data_sharing.settings import settings

T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    items: list[T] = Field([])
    nextPageToken: str = Field("")


class Share(BaseModel):
    name: str
    id: UUID4 | None = Field(None)


class ShareData(BaseModel):
    share: Share


class Schema(BaseModel):
    name: str
    share: str


class Table(BaseModel):
    id: UUID4
    name: str
    tableSchema: str = Field(alias="schema")
    share: str
    shareId: UUID4 = Field(None)


class TableVersion(BaseModel):
    deltaTableVersion: conint(ge=0) = Field(
        alias="delta-table-version", description=table_version_description
    )


class ProfileFile(BaseModel):
    shareCredentialsVersion: conint(ge=1) = Field(
        1, description=ProfileFileDescriptions.share_credentials_version
    )
    endpoint: AnyHttpUrl = Field(
        f"https://{settings.APP_DOMAIN}", description=ProfileFileDescriptions.endpoint
    )
    bearerToken: str = Field(description=ProfileFileDescriptions.bearer_token)
    expirationTime: datetime | None = Field(
        description=ProfileFileDescriptions.expiration_time
    )


class TableQueryRequest(BaseModel):
    predicateHints: list[str] = Field(None)
    jsonPredicateHints: str = Field(None)
    limitHint: conint(ge=0) = Field(None)
    version: conint(ge=0) = Field(None)
    timestamp: datetime = Field(None)
    startingVersion: conint(ge=0) = Field(None)
    endingVersion: conint(ge=0) = Field(None)

    model_config = {
        "json_schema_extra": {
            "examples": [{}],
        }
    }
