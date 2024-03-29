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

echo "--- ${BASE_DIR}/nii_dg ---"
mypy --strict \
    --allow-untyped-calls \
    --allow-untyped-decorators \
    --ignore-missing-imports \
    --no-warn-unused-ignores \
    --implicit-reexport \
    ${BASE_DIR}/nii_dg

echo "--- ${BASE_DIR}/schema/scripts ---"
mypy --strict \
    --allow-untyped-calls \
    --allow-untyped-decorators \
    --ignore-missing-imports \
    --no-warn-unused-ignores \
    --implicit-reexport \
    ${BASE_DIR}/schema/scripts

echo "--- ${BASE_DIR}/tests ---"
mypy --strict \
    --allow-untyped-calls \
    --allow-untyped-decorators \
    --ignore-missing-imports \
    --no-warn-unused-ignores \
    --implicit-reexport \
    ${BASE_DIR}/tests

echo "--- ${BASE_DIR}/setup.py ---"
mypy --strict \
    --allow-untyped-calls \
    --allow-untyped-decorators \
    --ignore-missing-imports \
    --no-warn-unused-ignores \
    --implicit-reexport \
    ${BASE_DIR}/setup.py
