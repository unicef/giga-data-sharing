from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

from data_sharing.settings import settings

header_scheme = APIKeyHeader(name="Authorization", scheme_name="Bearer")


def is_authenticated(token=Depends(header_scheme)):
    if token != settings.DELTA_BEARER_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
