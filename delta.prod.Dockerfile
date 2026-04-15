FROM eclipse-temurin:11-jdk-focal AS deps

ARG DELTA_SHARING_VERSION=1.3.10

RUN apt-get update && \
    apt-get install -y wget unzip curl && \
    apt-get clean

WORKDIR /build

# Download source
RUN wget "https://github.com/delta-io/delta-sharing/archive/refs/tags/v${DELTA_SHARING_VERSION}.zip" \
    -O source.zip && unzip source.zip

WORKDIR /build/delta-sharing-${DELTA_SHARING_VERSION}

RUN chmod +x build/sbt

RUN build/sbt server/universal:packageBin

RUN ZIP_FILE=$(ls server/target/universal/delta-sharing-server-*.zip) && \
    unzip "$ZIP_FILE" -d /build/output && \
    mv /build/output/delta-sharing-server-* /build/delta-sharing-server


FROM eclipse-temurin:11-jre-focal AS prod

WORKDIR /app

COPY --from=deps /build/delta-sharing-server ./

COPY ./delta-prod-docker-entrypoint.sh ./docker-entrypoint.sh
COPY ./conf-template ./conf

RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]