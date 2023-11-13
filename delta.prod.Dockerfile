FROM eclipse-temurin:17-jre-alpine as extract

WORKDIR /tmp

RUN wget https://github.com/delta-io/delta-sharing/releases/download/v1.0.2/delta-sharing-server-1.0.2.zip && \
    unzip delta-sharing-server-1.0.2.zip

FROM eclipse-temurin:17-jre-alpine as prod

WORKDIR /app

COPY --from=extract /tmp/delta-sharing-server-1.0.2 ./

CMD [ "./bin/delta-sharing-server", "--", "--config", "./conf/delta-sharing-server.yaml" ]
