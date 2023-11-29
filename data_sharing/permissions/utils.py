from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from .scheme import auth_scheme


def extract_sharing_key_components(
    key: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
) -> tuple[str, str]:
    split = key.credentials.split(":")
    if len(split) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized or malformed sharing key",
        )

    return split[0], split[1]
