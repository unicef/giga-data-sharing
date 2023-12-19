#!/bin/bash

sed -e "s|{{.STORAGE_ACCESS_KEY}}|$STORAGE_ACCESS_KEY|" \
    -e "s|{{.STORAGE_ACCOUNT_NAME}}|$STORAGE_ACCOUNT_NAME|" \
    -i conf/core-site.xml

sed -e "s!{{.DELTA_BEARER_TOKEN}}!$DELTA_BEARER_TOKEN!" \
    -e "s|{{.STORAGE_ACCOUNT_NAME}}|$STORAGE_ACCOUNT_NAME|" \
    -e "s|{{.CONTAINER_NAME}}|$CONTAINER_NAME|" \
    -e "s|{{.CONTAINER_PATH}}|$CONTAINER_PATH|" \
    -i conf/delta-sharing-server.yaml

exec ./bin/delta-sharing-server -- --config ./conf/delta-sharing-server.yaml
