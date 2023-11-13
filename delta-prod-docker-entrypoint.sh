#!/bin/bash

echo "$DELTA_SHARING_SERVER_YAML" > ./conf/delta-sharing-server.yaml
echo "$CORE_SITE_XML" > ./conf/core-site.xml

./bin/delta-sharing-server -- --config ./conf/delta-sharing-server.yaml
