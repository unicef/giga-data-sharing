#!/bin/sh

set -eu pipefail

poetry install --no-root --with dev
poetry run alembic upgrade head
poetry run python -m scripts.load_fixtures roles

exec poetry run uvicorn main:app --host 0.0.0.0 --port 5000 --reload
