from pydantic import UUID4, AwareDatetime, BaseModel, Field, conint


class Country(BaseModel):
    id: UUID4
    iso_3166_alpha_3: str
    name: str


class ApiKey(BaseModel):
    id: UUID4
    key: str
    expiration: AwareDatetime
    is_revoked: bool = Field(description="Indicates if the key was manually revoked.")
    permissions: list[Country]

    class Config:
        from_attributes = True


class CreateApiKeyRequest(BaseModel):
    validity: conint(ge=0) = Field(
        description=(
            "Validity of the API key in days. Set to 0 for no expiration (not"
            " recommended)."
        )
    )
    permissions: list[Country] = Field(
        description=(
            "List of countries, using the ISO-3166 alpha-3 code, to grant access to."
        )
    )

    class Config:
        from_attributes = True
