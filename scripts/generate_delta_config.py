from uuid import uuid4

import yaml
from loguru import logger

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.filedatalake import DataLakeServiceClient, PathProperties
from data_sharing.schemas.delta_sharing_config import Share, Table
from data_sharing.settings import settings

MASTER_SCHEMA_INDEX = 0
REFERENCE_SCHEMA_INDEX = 1
QOS_SCHEMA_INDEX = 2


def get_paths(root_path: str, are_directories: bool = False):
    service_client = DataLakeServiceClient(
        account_url=f"https://{settings.STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
        credential=settings.STORAGE_ACCESS_KEY,
    )
    fs_client = service_client.get_file_system_client(settings.CONTAINER_NAME)

    out = []

    try:
        logger.info(f"Looking in {root_path}...")
        for path in fs_client.get_paths(root_path, recursive=False):
            path: PathProperties
            condition = path.is_directory if are_directories else not path.is_directory

            if condition:
                name = path.name.split("/")[-1].split("_")[0].upper()
                out.append({"id": "", "name": name})
    except ResourceNotFoundError:
        pass

    return out


def get_available_countries():
    master = get_paths("updated_master_schema/master")
    master.append({"id": "", "name": "ZCDF"})

    reference = get_paths("updated_master_schema/reference")
    qos = get_paths("gold/qos", are_directories=True)

    return master, reference, qos


def enrich_id(country: dict[str, str], countries: list[dict[str, str]]):
    if country["name"] in [c["name"] for c in countries]:
        country["id"] = next(c["id"] for c in countries if c["name"] == country["name"])
    else:
        country["id"] = str(uuid4())


def enrich_master_reference_list():
    with open(settings.BASE_DIR / "scripts" / "countries.yaml") as f:
        countries: list[dict[str, str]] = yaml.safe_load(f)

    master, reference, qos = get_available_countries()

    unique_countries = {
        *[m["name"] for m in master],
        *[r["name"] for r in reference],
        *[q["name"] for q in qos],
    }

    for country in unique_countries:
        if country not in [c["name"] for c in countries]:
            countries.append({"id": str(uuid4()), "name": country})

    for country in master:
        enrich_id(country, countries)
    for country in reference:
        enrich_id(country, countries)
    for country in qos:
        enrich_id(country, countries)

    countries = sorted(countries, key=lambda x: x["name"])
    with open(settings.BASE_DIR / "scripts" / "countries.yaml", "w") as f:
        yaml.safe_dump(countries, f, indent=2)

    return (
        sorted(master, key=lambda x: x["name"]),
        sorted(reference, key=lambda x: x["name"]),
        sorted(qos, key=lambda x: x["name"]),
    )


def main():
    master, reference, qos = enrich_master_reference_list()

    with open(settings.BASE_DIR / "conf-template" / "delta-sharing-server.yaml") as f:
        config = yaml.safe_load(f)

    share = Share(**config["shares"][0])

    share.schemas[MASTER_SCHEMA_INDEX].tables = [
        Table(
            id=country["id"],
            name=country["name"],
            location=f"wasbs://{{{{.CONTAINER_NAME}}}}@{{{{.STORAGE_ACCOUNT_NAME}}}}.blob.core.windows.net/{{{{.CONTAINER_PATH}}}}/school_master.db/{country['name'].lower()}",
            historyShared=True,
        )
        for country in master
    ]

    share.schemas[REFERENCE_SCHEMA_INDEX].tables = [
        Table(
            id=country["id"],
            name=country["name"],
            location=f"wasbs://{{{{.CONTAINER_NAME}}}}@{{{{.STORAGE_ACCOUNT_NAME}}}}.blob.core.windows.net/{{{{.CONTAINER_PATH}}}}/school_reference.db/{country['name'].lower()}",
            historyShared=True,
        )
        for country in reference
    ]

    share.schemas[QOS_SCHEMA_INDEX].tables = [
        Table(
            id=country["id"],
            name=country["name"],
            location=f"wasbs://{{{{.CONTAINER_NAME}}}}@{{{{.STORAGE_ACCOUNT_NAME}}}}.blob.core.windows.net/{{{{.CONTAINER_PATH}}}}/qos.db/{country['name'].lower()}",
            historyShared=True,
        )
        for country in qos
    ]

    config["shares"][0] = share.model_dump(mode="json")

    with open(
        settings.BASE_DIR / "conf-template" / "delta-sharing-server.yaml", "w"
    ) as f:
        yaml.safe_dump(config, f, indent=2)


if __name__ == "__main__":
    main()
