import json
from pathlib import Path
from uuid import uuid4

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    with open(BASE_DIR / "scripts" / "countries.json", "r") as f:
        countries = json.load(f)

    with open(BASE_DIR / "conf-template" / "delta-sharing-server.yaml", "r") as f:
        config = yaml.safe_load(f)

    for country in countries:
        existing = next(
            (
                t
                for t in config["shares"][0]["schemas"][0]["tables"]
                if t["name"] == country
            ),
            None,
        )
        if not existing:
            config["shares"][0]["schemas"][0]["tables"].append(
                dict(
                    id=str(uuid4()),
                    name=country,
                    location=f"wasbs://{{{{.CONTAINER_NAME}}}}@{{{{.STORAGE_ACCOUNT_NAME}}}}.blob.core.windows.net/fake-gold/{country}-school_geolocation_coverage-master",
                    cdfEnabled=True,
                )
            )

    with open(BASE_DIR / "conf-template" / "delta-sharing-server.yaml", "w") as f:
        yaml.safe_dump(config, f, indent=2)


if __name__ == "__main__":
    main()
