FROM python:3.11 AS base

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

FROM base AS builder

ARG POETRY_VERSION=1.6.1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /tmp

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --without-hashes --without dev > requirements.txt

FROM base AS prod

WORKDIR /tmp

COPY --from=builder /tmp/requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

COPY . .

CMD [ "gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--config", "gunicorn.conf.py" ]
