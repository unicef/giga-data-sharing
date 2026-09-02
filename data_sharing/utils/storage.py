import asyncio

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.filedatalake import DataLakeServiceClient
from data_sharing.settings import settings

_service_client = DataLakeServiceClient(
    account_url=f"https://{settings.STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    credential=settings.STORAGE_ACCESS_KEY,
)
_fs_client = _service_client.get_file_system_client(settings.CONTAINER_NAME)


def _get_tables_with_data_sync(schema_name: str) -> set[str]:
    schema_dir = f"{settings.CONTAINER_PATH}/{schema_name.replace('-', '_')}.db"

    codes_with_data: set[str] = set()
    try:
        for path in _fs_client.get_paths(schema_dir, recursive=True):
            if path.is_directory:
                continue

            relative = path.name[len(schema_dir) :].lstrip("/")
            parts = relative.split("/")
            if len(parts) < 2 or parts[1] == "_delta_log":
                continue

            codes_with_data.add(parts[0].split("-")[0].upper())
    except ResourceNotFoundError:
        return set()

    return codes_with_data


async def get_tables_with_data(schema_name: str) -> set[str]:
    """Names of tables in `schema_name` that have an actual data file (i.e.
    something other than just a `_delta_log/` entry) present in storage,
    checked live against the storage account.
    """
    return await asyncio.to_thread(_get_tables_with_data_sync, schema_name)
