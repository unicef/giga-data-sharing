import asyncio
import os
import sys

import yaml
from loguru import logger
from sqlalchemy.dialects.postgresql import insert

from data_sharing import models
from data_sharing.db import get_db_context
from data_sharing.internal.hashing import get_key_hash
from data_sharing.models import ApiKey, Role
from data_sharing.schemas.api_key import ApiKey as ApiKeySchema
from data_sharing.settings import settings


async def main(fixtures: list[str]):
    sum_data = 0
    for fixture in fixtures:
        fixture_file = (
            settings.BASE_DIR / "data_sharing" / "fixtures" / f"{fixture}.yaml"
        )
        if not fixture_file.exists():
            raise FileNotFoundError(f"Fixture `{fixture}` could not be found.")

        with open(fixture_file, "r") as f:
            data = yaml.safe_load(f)

        try:
            model = getattr(models, data[0]["model"])
        except AttributeError:
            raise AttributeError(f"Model `{data['model']}` could not be found.")

        async with get_db_context() as session:
            await session.execute(
                insert(model)
                .values([{**d["fields"], "id": d["id"]} for d in data])
                .on_conflict_do_nothing()
            )
            await session.commit()

        sum_data += len(data)

    api_key_id = os.environ.get("ADMIN_API_KEY")
    api_key_secret = os.environ.get("ADMIN_API_SECRET")
    if api_key_id and api_key_secret:
        (admin_role,) = session.query(Role).filter(Role.id == "ADMIN").first()
        admin_key = ApiKeySchema(
            id=api_key_id,
            secret=get_key_hash(api_key_secret),
            expiration=None,
            roles={admin_role},
            description="Admin API Key",
        )
        async with get_db_context() as session:
            await session.execute(
                insert(ApiKey).values([admin_key.model_dump()]).on_conflict_do_nothing()
            )
            await session.commit()
        sum_data += 1

    logger.info(f"Installed {sum_data} rows from {len(fixtures)} fixtures.")


if __name__ == "__main__":
    if len(args := sys.argv[1:]) == 0:
        raise ValueError("At least one fixture must be specified.")

    asyncio.run(main(args))