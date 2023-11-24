from datetime import datetime
from typing import Dict, Generic, Optional, TypeVar, Union

from pydantic import UUID4, AnyHttpUrl, BaseModel, Field, conint


class Format(BaseModel):
    provider: str
    options: Optional[Dict[str, str]] = None


class Protocol(BaseModel):
    minReaderVersion: conint(ge=1)
    minWriterVersion: conint(ge=1)
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
    configuration: Dict[str, str]


class MetadataWrapper(BaseModel):
    deltaMetadata: Metadata
    version: Optional[conint(ge=1)] = Field(None)
    size: Optional[conint(ge=0)] = Field(None)
    numFiles: Optional[conint(ge=0)] = Field(None)


class DeletionVector(BaseModel):
    storageType: str
    pathOrInlineDv: str
    offSet: Optional[int] = Field(None)
    sizeINBytes: Optional[int] = Field(None)
    cardinality: Optional[conint(ge=0)] = Field(None)


class Add(BaseModel):
    path: str
    partitionValues: Dict[str, str]
    size: conint(ge=0)
    modificationTime: conint(ge=0)
    dataChange: bool
    stats: Optional[str] = Field(None)
    tags: Optional[Dict[str, str]] = Field(None)
    deletionVector: Optional[DeletionVector] = Field(None)
    baseRowId: Optional[conint(ge=0)] = Field(None)
    defaultRowCommitVersion: Optional[conint(ge=0)] = Field(None)
    clusteringProvider: Optional[str] = Field(None)


class Remove(BaseModel):
    path: str
    deletionTimestamp: Optional[conint(ge=0)] = Field(None)
    dataChange: bool
    extendedFileMetadata: Optional[bool]
    partitionValues: Optional[Dict[str, str]] = Field(None)
    size: Optional[conint(ge=0)] = Field(None)
    stats: Optional[str] = Field(None)
    tags: Optional[Dict[str, str]] = Field(None)
    DeletionVector: Optional[DeletionVector] = Field(None)
    baseRowId: Optional[conint(ge=0)] = Field(None)
    defaultRowCommitVersion: Optional[conint(ge=0)] = Field(None)


class CDC(BaseModel):
    path: str
    partitionValues: Dict[str, str]
    size: conint(ge=0)
    dataChange: bool
    tags: Dict[str, str]


class FileWrapper(BaseModel):
    id: str
    deletionVectorFileId: Optional[str] = Field(None)
    version: Optional[conint(ge=1)] = Field(None)
    timestamp: Optional[conint(ge=0)] = Field(None)
    expirationTimestamp: Optional[conint(ge=0)] = Field(None)
    deltaSingleAction: Union[Add, Remove, CDC]
