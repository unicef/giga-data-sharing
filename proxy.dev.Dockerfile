FROM python:3.11

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ARG POETRY_VERSION=1.6.1

RUN pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry config installer.max-workers 4

WORKDIR /app

ENTRYPOINT [ "/app/proxy-dev-docker-entrypoint.sh" ]
