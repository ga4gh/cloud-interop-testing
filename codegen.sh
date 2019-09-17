#!/usr/bin/env bash

set -v

OPENAPI_PATH=ga4ghtest/openapi/openapi.yaml
PACKAGE_NAME="ga4ghtest"
PACKAGE_VERSION="0.3.0"
PACKAGE_FOLDER="."

cat << EOF > .openapi-generator-config
{
  "packageName": "$PACKAGE_NAME",
  "packageVersion": "$PACKAGE_VERSION"
}
EOF


# docker run --rm \
#     -v ${PWD}:/local openapitools/openapi-generator-cli generate \
#     -c /local/.openapi-generator-config \
#     -t /local/.codegen/server \
#     -Dmodels \
#     -DmodelTests=false \
#     -Dapis \
#     -DapiTests=false \
#     -i /local/synprov/openapi/openapi.yaml \
#     -g python-flask \
#     -o /local/

npx openapi-generator generate \
    -c .openapi-generator-config \
    -t .codegen/server \
    -Dmodels \
    -DmodelTests=false \
    -Dapis \
    -DapiTests=false \
    -i ${OPENAPI_PATH} \
    -g python-flask \
    -o "${PACKAGE_FOLDER}"

# npx openapi-generator generate \
#     -i ${SWAGGER_PATH} \
#     -g python \
#     -o "${PACKAGE_FOLDER}" \
#     -DgenerateSourceCodeOnly=true \
#     -DpackageName="${NAMESPACE}.${PACKAGE_NAME}.client" \
#     -DpackageVersion="${PACKAGE_VERSION}"

# mv "${PACKAGE_FOLDER}/${NAMESPACE}/${PACKAGE_NAME}/client_README.md" ${PACKAGE_FOLDER}/