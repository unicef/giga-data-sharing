from typing import Any


def _stringify(value: Any) -> str:
    return str(value).lower() if isinstance(value, bool) else str(value)


def query_parametrize(params: dict[str, Any]):
    return "&".join(
        [f"{k}={_stringify(v)}" for k, v in params.items() if v is not None]
    )
