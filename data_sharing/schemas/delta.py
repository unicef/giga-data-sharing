from typing import Optional

from pydantic import UUID4, BaseModel, Field, conint


class Format(BaseModel):
    provider: str
    options: Optional[dict[str, str]] = None


class Protocol(BaseModel):
    minReaderVersion: conint(ge=0)
    minWriterVersion: conint(ge=0)
    readerFeatures: Optional[list[str]] = Field(None)
    writerFeatures: Optional[list[str]] = Field(None)


class ProtocolWrapper(BaseModel):
    deltaProtocol: Protocol


class Metadata(BaseModel):
    id: UUID4
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    format: Format
    schemaString: str
    partitionColumns: list[str]
    createdTime: Optional[conint(ge=0)] = Field(None)
    configuration: dict[str, str]


class MetadataWrapper(BaseModel):
    deltaMetadata: Metadata
    version: Optional[conint(ge=0)] = Field(None)
    size: Optional[conint(ge=0)] = Field(None)
    numFiles: Optional[conint(ge=0)] = Field(None)


class DeletionVector(BaseModel):
    storageType: str
    pathOrInlineDv: str
    offSet: Optional[int] = Field(None)
    sizeInBytes: Optional[int] = Field(None)
    cardinality: Optional[conint(ge=0)] = Field(None)


class Add(BaseModel):
    path: str
    partitionValues: dict[str, str]
    size: conint(ge=0)
    modificationTime: conint(ge=0)
    dataChange: bool
    stats: Optional[str] = Field(None)
    tags: Optional[dict[str, str]] = Field(None)
    deletionVector: Optional[DeletionVector] = Field(None)
    baseRowId: Optional[conint(ge=0)] = Field(None)
    defaultRowCommitVersion: Optional[conint(ge=0)] = Field(None)
    clusteringProvider: Optional[str] = Field(None)


class AddWrapper(BaseModel):
    add: Add


class Remove(BaseModel):
    path: str
    deletionTimestamp: Optional[conint(ge=0)] = Field(None)
    dataChange: bool
    extendedFileMetadata: Optional[bool]
    partitionValues: Optional[dict[str, str]] = Field(None)
    size: Optional[conint(ge=0)] = Field(None)
    stats: Optional[str] = Field(None)
    tags: Optional[dict[str, str]] = Field(None)
    deletionVector: Optional[DeletionVector] = Field(None)
    baseRowId: Optional[conint(ge=0)] = Field(None)
    defaultRowCommitVersion: Optional[conint(ge=0)] = Field(None)


class RemoveWrapper(BaseModel):
    remove: Remove


class CDC(BaseModel):
    path: str
    partitionValues: dict[str, str]
    size: conint(ge=0)
    dataChange: bool
    tags: dict[str, str]


class CDCWrapper(BaseModel):
    cdc: CDC


class File(BaseModel):
    id: str
    deletionVectorFileId: Optional[str] = Field(None)
    version: Optional[conint(ge=0)] = Field(None)
    timestamp: Optional[conint(ge=0)] = Field(None)
    expirationTimestamp: Optional[conint(ge=0)] = Field(None)
    deltaSingleAction: AddWrapper | RemoveWrapper | CDCWrapper


class FileWrapper(BaseModel):
    file: File


class TableMetadataResponse(BaseModel):
    protocol: ProtocolWrapper
    metaData: MetadataWrapper


class TableDataResponse(TableMetadataResponse):
    files: list[File]


class TableDataChangeResponse(TableMetadataResponse):
    files: list[FileWrapper]
