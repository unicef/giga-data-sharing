FROM maven:3.9-eclipse-temurin-11-focal AS deps

ARG DELTA_SHARING_VERSION=1.0.4

RUN apt update && \
    apt install -y wget unzip && \
    apt clean

WORKDIR /tmp

RUN wget "https://github.com/delta-io/delta-sharing/releases/download/v$DELTA_SHARING_VERSION/delta-sharing-server-$DELTA_SHARING_VERSION.zip" && \
    unzip "delta-sharing-server-$DELTA_SHARING_VERSION.zip" && \
    mv "delta-sharing-server-$DELTA_SHARING_VERSION" delta-sharing-server

FROM eclipse-temurin:11-jre-alpine as prod

RUN apk add --no-cache bash libc6-compat

WORKDIR /app

COPY --from=deps /tmp/delta-sharing-server ./
COPY ./delta-prod-docker-entrypoint.sh ./docker-entrypoint.sh
COPY ./conf-template ./conf

ENTRYPOINT [ "./docker-entrypoint.sh" ]
