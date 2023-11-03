from datetime import datetime
from typing import Generic, TypeVar

from pydantic import UUID4, AnyHttpUrl, BaseModel, Field, conint

T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    items: list[T]
    nextPageToken: str | None = Field("")


class Share(BaseModel):
    name: str
    id: UUID4 | None = Field(None)


class Schema(BaseModel):
    name: str
    share: str


class Table(BaseModel):
    id: UUID4
    name: str
    schema: str
    share: str
    shareId: UUID4 | None = Field(None)


class TableVersion(BaseModel):
    deltaTableVersion: str = Field(alias="delta-table-version")


class Protocol(BaseModel):
    minReaderVersion: conint(ge=1)


class Format(BaseModel):
    provider: str


class Metadata(BaseModel):
    id: UUID4
    name: str | None = Field(None)
    description: str | None = Field(None)
    format: Format
    schemaString: str
    partitionColumns: list[str]
    configuration: dict[str, str]
    version: int | None = Field(None)
    size: int | None = Field(None)
    numFile: int | None = Field(None)


class File(BaseModel):
    id: UUID4
    url: AnyHttpUrl
    partitionValues: dict[str, str]
    size: int
    stats: str | None = Field(None)
    version: int | None = Field(None)
    timestamp: int | None = Field(None)
    expirationTimestamp: int | None = Field(None)


class TableMetadataResponse(BaseModel):
    protocol: Protocol
    metaData: Metadata


class TableDataResponse(TableMetadataResponse):
    files: list[File]


class TableQueryRequest(BaseModel):
    predicateHints: list[str] | None = Field(None)
    jsonPredicateHints: str | None = Field(None)
    limitHint: int | None = Field(None)
    version: conint(ge=1) | None = Field(None)
    timestamp: datetime | None = Field(None)
    startingVersion: int | None = Field(None)
    endingVersion: int | None = Field(None)
