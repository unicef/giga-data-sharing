def parse_capabilities_header(header: str) -> dict[str, str]:
    splits = [h.strip() for h in header.split(",")]
    return {
        key.strip(): value.strip()
        for split in splits
        for key, value in split.split("=")
    }


def create_capabilities_header(header: dict[str, str]) -> str:
    return ",".join([f"{key}={value}" for key, value in header.items()])
