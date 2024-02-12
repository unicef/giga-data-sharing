FROM eclipse-temurin:11-jre-alpine

ARG DELTA_SHARING_VERSION=1.0.4

WORKDIR /tmp

RUN wget "https://github.com/delta-io/delta-sharing/releases/download/v$DELTA_SHARING_VERSION/delta-sharing-server-$DELTA_SHARING_VERSION.zip" && \
    unzip "delta-sharing-server-$DELTA_SHARING_VERSION.zip" && \
    cp "/tmp/delta-sharing-server-$DELTA_SHARING_VERSION" /app

WORKDIR /app

COPY ./delta-prod-docker-entrypoint.sh docker-entrypoint.sh
COPY ./conf-template ./conf

ENTRYPOINT [ "./docker-entrypoint.sh" ]
