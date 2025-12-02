from pydantic import UUID4, AwareDatetime, BaseModel, Field, conint, constr

from data_sharing.annotations.api_key import ApiKeyDescriptions


class Schema(BaseModel):
    id: constr(min_length=1, max_length=50)
    description: str = Field(None)


class Role(BaseModel):
    id: constr(min_length=3, max_length=5)
    description: str = Field(None)


class SafeApiKey(BaseModel):
    key_id: UUID4 = Field(alias="id")
    created: AwareDatetime
    description: str = Field(None)
    expiration: AwareDatetime | None
    roles: list[Role]
    schemas: list[Schema]

    class Config:
        from_attributes = True


class ApiKey(SafeApiKey):
    key_secret: str = Field(alias="secret")


class CreateApiKeyRequest(BaseModel):
    description: str = Field(description=ApiKeyDescriptions.description)
    validity: conint(ge=0) = Field(description=ApiKeyDescriptions.validity)
    schemas: list[str] = Field(default=[], description="List of schemas to grant access to")
    roles: list[str] = Field(description=ApiKeyDescriptions.roles, default=[])

    class Config:
        from_attributes = True


class UpdateApiKeyRequest(BaseModel):
    schemas: list[str] = Field(default=[], description="List of schemas to grant access to")
    roles: list[str] = Field(default=[], description="List of roles (countries) to grant access to")
