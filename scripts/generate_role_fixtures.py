from pathlib import Path

import yaml
from country_converter import CountryConverter

BASE_DIR = Path(__file__).resolve().parent.parent

coco = CountryConverter()


def main():
    with open(BASE_DIR / "scripts" / "countries.yaml", "r") as f:
        countries = yaml.safe_load(f)

    roles = [
        {"id": "ADMIN", "model": "Role", "fields": {"description": "Administrator"}}
    ]
    for country in countries:
        if country["name"] == "CDF":
            roles.append(
                {
                    "id": "CDF",
                    "model": "Role",
                    "fields": {"description": "cdf_test"},
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

    with open(BASE_DIR / "data_sharing" / "fixtures" / "roles.yaml", "w") as f:
        yaml.dump(roles, f, indent=2, allow_unicode=True)


if __name__ == "__main__":
    main()
