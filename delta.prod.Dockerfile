FROM eclipse-temurin:17-jre-alpine as extract

WORKDIR /tmp

RUN wget https://github.com/delta-io/delta-sharing/releases/download/v1.0.2/delta-sharing-server-1.0.2.zip && \
    unzip delta-sharing-server-1.0.2.zip

FROM eclipse-temurin:17-jre-alpine as prod

WORKDIR /app

COPY --from=extract /tmp/delta-sharing-server-1.0.2 ./
COPY delta-prod-docker-entrypoint.sh docker-entrypoint.sh
COPY ./conf-template ./conf

CMD [ "./docker-entrypoint.sh" ]
