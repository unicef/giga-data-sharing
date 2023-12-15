from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    with open(BASE_DIR / "scripts" / "countries.yaml", "r") as f:
        countries = yaml.safe_load(f)

    with open(BASE_DIR / "conf-template" / "delta-sharing-server.yaml", "r") as f:
        config = yaml.safe_load(f)

    for index, _ in enumerate(config["shares"][0]["schemas"]):
        config["shares"][0]["schemas"][index]["tables"] = [
            dict(
                id=country["id"],
                name=country["name"],
                location=f"wasbs://{{{{.CONTAINER_NAME}}}}@{{{{.STORAGE_ACCOUNT_NAME}}}}.blob.core.windows.net/{{{{.CONTAINER_PATH}}}}/school-reference/{country['name']}",
                historyShared=True,
            )
            for country in countries
        ]

    with open(BASE_DIR / "conf-template" / "delta-sharing-server.yaml", "w") as f:
        yaml.safe_dump(config, f, indent=2)


if __name__ == "__main__":
    main()
