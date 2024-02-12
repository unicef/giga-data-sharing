FROM maven:3.9-eclipse-temurin-11-alpine AS base

FROM base AS build

WORKDIR /tmp/custom-sas-provider

COPY ./custom-sas-provider ./

RUN mvn clean package

FROM base AS dev

WORKDIR /tmp

RUN wget https://github.com/delta-io/delta-sharing/releases/download/v1.0.4/delta-sharing-server-1.0.4.zip && \
    unzip delta-sharing-server-1.0.4.zip

WORKDIR /app

RUN cp -R /tmp/delta-sharing-server-1.0.4/* ./

CMD [ "./bin/delta-sharing-server", "--", "--config", "./conf/delta-sharing-server.yaml" ]
