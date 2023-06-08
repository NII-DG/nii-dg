#!/usr/bin/env bash

# This script is used to test the load of the REST API server.
# It sends multiple POST requests to the server and then fetches the results.

set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "${HERE}/.." && pwd)
DEV_COMPOSE_FILE="${ROOT_DIR}/compose.dev.yml"
REQUEST_COUNT=20

VALID_CRATE_FILE="${ROOT_DIR}/tests/example/sample_crate.json"
INVALID_CRATE_FILE="${ROOT_DIR}/tests/example/invalid_crate1.json"

cd "${ROOT_DIR}"

# trap to stop services in case of error
trap 'docker compose -f "${DEV_COMPOSE_FILE}" down >/dev/null && echo "Test failed." && exit 1' ERR

# Function to start services
start_services() {
  echo "=== Starting NII-DG dev env using docker compose ... ==="
  docker compose -f "${DEV_COMPOSE_FILE}" down >/dev/null
  docker compose -f "${DEV_COMPOSE_FILE}" up -d
}

# Function to send load test requests
send_requests() {
  local CRATE_FILE=$1
  local RESULT_STATUS=$2
  declare -A REQUEST_IDS=()

  for i in $(seq 1 "${REQUEST_COUNT}"); do
    REQUEST_ID=$(curl -sS -X POST -H "Content-Type: application/json" -d "@${CRATE_FILE}" localhost:5000/validate | jq -r .request_id)
    echo "Sent request ${i} with request_id: ${REQUEST_ID} and crate file: ${CRATE_FILE##*/}"

    # Store the request_id in the array
    REQUEST_IDS[${REQUEST_ID}]=1
  done

  # Wait for all the requests to complete
  for REQUEST_ID in "${!REQUEST_IDS[@]}"; do
    while true; do
      RESULT=$(curl -sS "localhost:5000/${REQUEST_ID}" | jq -r .status)

      if [[ "$RESULT" == "QUEUED" || "$RESULT" == "RUNNING" ]]; then
        sleep 1
      else
        echo "Request ${REQUEST_ID} completed with status: ${RESULT}"
        if [[ "$RESULT" != "${RESULT_STATUS}" ]]; then
          echo "Request ${REQUEST_ID} failed. (status is not ${RESULT_STATUS})"
          exit 1
        fi
        break
      fi
    done
  done
}

# Test the load using different server configurations
test_server_load() {
  local SERVER_NAME=$1
  local THREAD_COUNT=$2

  echo "=== Testing the load using ${SERVER_NAME} server (with THREADS=${THREAD_COUNT}) ... ==="
  # Clean environment
  docker compose -f "${DEV_COMPOSE_FILE}" restart app >/dev/null
  docker compose -f "${DEV_COMPOSE_FILE}" exec \
    -d \
    -e DG_WSGI_SERVER=${SERVER_NAME} \
    -e DG_WSGI_THREADS=${THREAD_COUNT} \
    app python3 ./nii_dg/api.py
  sleep 3
  curl -sS localhost:5000/healthcheck >/dev/null

  send_requests "${VALID_CRATE_FILE}" "COMPLETE"
  send_requests "${INVALID_CRATE_FILE}" "FAILED"
}

# Start services
start_services

# Test the load using Flask server
test_server_load "flask" "1"

# Test the load using waitless server with 1 thread
test_server_load "waitless" "1"

# Test the load using waitless server with 3 threads
test_server_load "waitless" "3"
