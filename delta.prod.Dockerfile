FROM maven:3.9-eclipse-temurin-11-alpine as build

WORKDIR /tmp/custom-sas-provider

COPY ./custom-sas-provider ./

RUN mvn clean package

FROM eclipse-temurin:11-jre-alpine as extract

WORKDIR /tmp

RUN wget https://github.com/delta-io/delta-sharing/releases/download/v1.0.2/delta-sharing-server-1.0.2.zip && \
    unzip delta-sharing-server-1.0.2.zip

FROM eclipse-temurin:11-jre-alpine as prod

WORKDIR /app

COPY --from=extract /tmp/delta-sharing-server-1.0.2 ./
COPY --from=build /tmp/custom-sas-provider/target/custom-sas-provider-1.0-SNAPSHOT.jar ./lib/internal.giga.customSasProvider.custom-sas-provider-1.0-SNAPSHOT.jar
COPY ./delta-prod-docker-entrypoint.sh docker-entrypoint.sh
COPY ./conf-template ./conf

CMD [ "/app/docker-entrypoint.sh" ]
