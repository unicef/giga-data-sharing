from fastapi.security import APIKeyHeader

header_scheme = APIKeyHeader(
    name="X-Giga-Sharing-Key",
    description="Sharing key in the following format: `{api_key_id}:{api_key_secret}`",
)
