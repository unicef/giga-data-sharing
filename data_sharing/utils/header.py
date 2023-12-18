def parse_capabilities_header(header: str | None) -> dict[str, str]:
    if header is None:
        return {}

    splits = [h.strip() for h in header.split(";")]
    parsed = {}
    for split in splits:
        key, value = split.split("=")
        parsed[key.strip()] = value.strip()
    return parsed


def create_capabilities_header(header: dict[str, str]) -> str:
    return ",".join([f"{key}={value}" for key, value in header.items()])
