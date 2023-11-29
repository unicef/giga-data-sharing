from fastapi import Depends, HTTPException
from starlette import status

from .scheme import header_scheme


def extract_sharing_key_components(
    key=Depends(header_scheme),
) -> tuple[str, str]:
    split = key.split(":")
    if len(split) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized or malformed sharing key",
        )

    return split
