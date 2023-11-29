FROM maven:3.9-eclipse-temurin-11-alpine as base

FROM base as build

WORKDIR /tmp/custom-sas-provider

COPY ./custom-sas-provider ./

RUN mvn clean package

FROM base as dev

WORKDIR /tmp

RUN wget https://github.com/delta-io/delta-sharing/releases/download/v1.0.2/delta-sharing-server-1.0.2.zip && \
    unzip delta-sharing-server-1.0.2.zip

WORKDIR /app

RUN cp -R /tmp/delta-sharing-server-1.0.2/* ./

COPY --from=build /tmp/custom-sas-provider/target/custom-sas-provider-1.0-SNAPSHOT.jar ./lib/internal.giga.customSasProvider.custom-sas-provider-1.0-SNAPSHOT.jar

CMD [ "./bin/delta-sharing-server", "--", "--config", "./conf/delta-sharing-server.yaml" ]
