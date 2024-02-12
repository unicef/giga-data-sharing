FROM eclipse-temurin:11-jre-jammy

ARG DELTA_SHARING_VERSION=1.0.4

WORKDIR /tmp

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget unzip && \
    wget "https://github.com/delta-io/delta-sharing/releases/download/v$DELTA_SHARING_VERSION/delta-sharing-server-$DELTA_SHARING_VERSION.zip" && \
    unzip "delta-sharing-server-$DELTA_SHARING_VERSION.zip" && \
    cp -r "/tmp/delta-sharing-server-$DELTA_SHARING_VERSION" /app && \
    apt-get clean

WORKDIR /app

COPY ./delta-prod-docker-entrypoint.sh ./docker-entrypoint.sh
COPY ./conf-template ./conf

CMD [ "./docker-entrypoint.sh" ]
