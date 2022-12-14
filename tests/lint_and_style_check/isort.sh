#!/usr/bin/env bash
set -eu

SCRIPT_DIR=$(
    cd $(dirname $0)
    pwd
)
BASE_DIR=$(
    cd ${SCRIPT_DIR}/../..
    pwd
)

cd ${BASE_DIR}

isort ${BASE_DIR} \
    --check
