FROM maven:3.9-eclipse-temurin-11-focal

RUN apt update && \
    apt install -y wget unzip && \
    apt clean

ARG DELTA_SHARING_VERSION=1.0.4

WORKDIR /tmp

RUN wget "https://github.com/delta-io/delta-sharing/releases/download/v$DELTA_SHARING_VERSION/delta-sharing-server-$DELTA_SHARING_VERSION.zip" && \
    unzip "delta-sharing-server-$DELTA_SHARING_VERSION.zip"

WORKDIR /app

RUN cp -R /tmp/delta-sharing-server-$DELTA_SHARING_VERSION/* ./

CMD [ "./bin/delta-sharing-server", "--", "--config", "./conf/delta-sharing-server.yaml" ]
