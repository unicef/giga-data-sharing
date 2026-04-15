FROM eclipse-temurin:11-jdk-focal AS builder

RUN apt-get update && apt-get install -y wget unzip curl

RUN curl -L https://github.com/sbt/sbt/releases/download/v1.9.7/sbt-1.9.7.tgz | tar zx -C /usr/local && \
    ln -s /usr/local/sbt/bin/sbt /usr/local/bin/sbt

ARG DELTA_SHARING_VERSION=1.3.10

WORKDIR /build

RUN wget "https://github.com/delta-io/delta-sharing/archive/refs/tags/v${DELTA_SHARING_VERSION}.zip" \
    -O source.zip && unzip source.zip

WORKDIR /build/delta-sharing-${DELTA_SHARING_VERSION}

RUN sbt "project server" "universal:packageBin"

RUN ZIP_FILE=$(ls server/target/universal/delta-sharing-server-*.zip) && \
    unzip "$ZIP_FILE" -d /output && \
    mv /output/delta-sharing-server-* /output/server

FROM eclipse-temurin:11-jre-focal

WORKDIR /app

COPY --from=builder /output/server ./

CMD ["./bin/delta-sharing-server", "--config", "./conf/delta-sharing-server.yaml"]