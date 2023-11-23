from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import UUID4, AnyHttpUrl, BaseModel, Field, conint

T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    items: list[T]
    nextPageToken: str = Field("")


class Share(BaseModel):
    name: str
    id: Optional[UUID4] = Field(None)


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
    deltaTableVersion: str = Field(alias="delta-table-version")


class Protocol(BaseModel):
    minReaderVersion: conint(ge=1)


class Format(BaseModel):
    provider: str


class Metadata(BaseModel):
    id: UUID4
    name: str = Field(None)
    description: str = Field(None)
    format: Format
    schemaString: str
    partitionColumns: list[str]
    configuration: dict[str, str]
    version: conint(ge=1) = Field(None)
    size: conint(ge=0) = Field(None)
    numFile: conint(ge=0) = Field(None)


class File(BaseModel):
    id: str
    url: AnyHttpUrl
    partitionValues: dict[str, str]
    size: conint(ge=0)
    stats: str = Field(None)
    version: conint(ge=1) = Field(None)
    timestamp: conint(ge=0) = Field(None)
    expirationTimestamp: conint(ge=0) = Field(None)


class ProfileFile(BaseModel):
    shareCredentialsVersion: int
    endpoint: str
    bearerToken: str
    expirationTimestamp: datetime


class TableMetadataResponse(BaseModel):
    protocol: Protocol
    metaData: Metadata


class TableDataResponse(TableMetadataResponse):
    files: list[File]


class TableQueryRequest(BaseModel):
    predicateHints: list[str] = Field(None)
    jsonPredicateHints: str = Field(None)
    limitHint: int = Field(None)
    version: conint(ge=1) = Field(None)
    timestamp: datetime = Field(None)
    startingVersion: conint(ge=1) = Field(None)
    endingVersion: conint(ge=1) = Field(None)


class Error(BaseModel):
    errorCode: str = Field("")
    message: str = Field("")
