from pydantic import UUID4, BaseModel, Field


class Table(BaseModel):
    id: UUID4
    name: str
    location: str
    historyShared: bool = Field(True)


class Schema(BaseModel):
    name: str
    tables: list[Table]


class Share(BaseModel):
    id: UUID4
    name: str
    schemas: list[Schema]
