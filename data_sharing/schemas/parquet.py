from pydantic import UUID4, AnyHttpUrl, BaseModel, Field, conint


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
    configuration: dict[str, str] = Field(None)
    version: conint(ge=0) | None = Field(None)
    size: conint(ge=0) | None = Field(None)
    numFile: conint(ge=0) | None = Field(None)


class File(BaseModel):
    id: str
    url: AnyHttpUrl
    partitionValues: dict[str, str]
    size: conint(ge=0)
    stats: str | None = Field(None)
    version: conint(ge=0) = Field(None)
    timestamp: conint(ge=0) | None = Field(None)
    expirationTimestamp: conint(ge=0) | None = Field(None)


class CDFDetail(BaseModel):
    id: str
    url: AnyHttpUrl
    partitionValues: dict[str, str]
    size: conint(ge=0)
    timestamp: conint(ge=0) = Field(None)
    version: conint(ge=0) = Field(None)
    expirationTimestamp: conint(ge=0) | None = Field(None)


class CDF(BaseModel):
    cdf: CDFDetail


class RemoveDetail(CDFDetail):
    pass


class Remove(BaseModel):
    remove: RemoveDetail


class AddDetail(CDFDetail):
    stats: str | None = Field(None)


class Add(BaseModel):
    add: AddDetail


class TableMetadataResponse(BaseModel):
    protocol: Protocol
    metaData: Metadata


class TableDataResponse(TableMetadataResponse):
    files: list[File]


class TableDataChangeResponse(TableMetadataResponse):
    files: list[Add | Remove | CDF]
