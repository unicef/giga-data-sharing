from pathlib import Path

import yaml
from country_converter import CountryConverter
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent.parent

coco = CountryConverter()


def main():
    with open(BASE_DIR / "scripts" / "countries.yaml") as f:
        countries = yaml.safe_load(f)

    roles = [
        {"id": "ADMIN", "model": "Role", "fields": {"description": "Administrator"}}
    ]
    for country in countries:
        if country["name"] == "ZCDF":
            roles.append(
                {
                    "id": "ZCDF",
                    "model": "Role",
                    "fields": {"description": "CDF test"},
                }
            )
        else:
            roles.append(
                {
                    "id": country["name"],
                    "model": "Role",
                    "fields": {"description": coco.convert(country["name"], to="name")},
                }
            )

    role_fixtures_path = BASE_DIR / "data_sharing" / "fixtures" / "roles.yaml"
    with open(role_fixtures_path, "w") as f:
        yaml.dump(roles, f, indent=2, allow_unicode=True)

    logger.info(f"Created fixture for {len(roles)} roles in {role_fixtures_path}")


if __name__ == "__main__":
    main()
