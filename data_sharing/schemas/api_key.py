from pydantic import UUID4, AwareDatetime, BaseModel, Field, conint, constr

from data_sharing.annotations.api_key import ApiKeyDescriptions


class Role(BaseModel):
    id: constr(min_length=3, max_length=5)  # Supports e.g., 'KEN', 'SCHM', 'ADMIN'
    description: str = Field(None)


class SafeApiKey(BaseModel):
    key_id: UUID4 = Field(alias="id")
    created: AwareDatetime
    description: str = Field(None)
    expiration: AwareDatetime | None
    roles: list[Role]

    class Config:
        from_attributes = True


class ApiKey(SafeApiKey):
    key_secret: str = Field(alias="secret")


class CreateApiKeyRequest(BaseModel):
    description: str = Field(description=ApiKeyDescriptions.description)
    validity: conint(ge=0) = Field(description=ApiKeyDescriptions.validity)
    roles: list[str] = Field(description=ApiKeyDescriptions.roles)

    class Config:
        from_attributes = True
