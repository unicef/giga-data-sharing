from fastapi.security import HTTPBearer

auth_scheme = HTTPBearer(
    description="The `bearerToken` in the Profile File that you were provided"
)
