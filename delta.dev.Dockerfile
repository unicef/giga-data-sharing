FROM eclipse-temurin:17-jre-alpine

WORKDIR /tmp

RUN wget https://github.com/delta-io/delta-sharing/releases/download/v1.0.2/delta-sharing-server-1.0.2.zip && \
    unzip delta-sharing-server-1.0.2.zip

WORKDIR /app

RUN cp -R /tmp/delta-sharing-server-1.0.2/* ./

CMD [ "./bin/delta-sharing-server", "--", "--config", "./conf/delta-sharing-server.yaml" ]
