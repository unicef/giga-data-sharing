from pydantic import (
    UUID4,
    AwareDatetime,
    BaseModel,
    Field,
    conint,
    constr,
    field_serializer,
)

from data_sharing.annotations.api_key import ApiKeyDescriptions


class Role(BaseModel):
    id: constr(min_length=3, max_length=5)
    description: str = Field(None)


class SafeApiKey(BaseModel):
    id: UUID4
    created: AwareDatetime
    description: str = Field(None)
    key: str = Field(description=ApiKeyDescriptions.key)
    expiration: AwareDatetime
    roles: list[Role]

    class Config:
        from_attributes = True

    @field_serializer("key")
    def serialize_key(self, key: str, _info):
        return key.ljust(24, "*")


class ApiKey(SafeApiKey):
    hashed_key: str


class CreateApiKeyRequest(BaseModel):
    description: str = Field(
        description="Describe what this API key will be used for or who will use it",
    )
    validity: conint(ge=0) = Field(
        description=(
            "Validity of the API key in days. Set to 0 for no expiration (not"
            " recommended)"
        )
    )
    roles: list[str] = Field(
        description=(
            "List of countries, using the ISO-3166 alpha-3 code, to grant access to"
        )
    )

    class Config:
        from_attributes = True
