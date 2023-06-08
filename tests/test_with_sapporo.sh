#!/usr/bin/env bash

# This script tests the interaction of NII-DG and Sapporo services.
# It uses docker-compose to start both services, runs a workflow, validates the result and finally cleans up.

# Dependencies:
#   - docker
#   - docker compose
#   - python3 (with NII-DG library)
#   - jq
#   - curl

set -eu
set -o pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "${HERE}/.." && pwd)
SAPPORO_EXAMPLE_DIR="${ROOT_DIR}/sapporo_example"

cd "${SAPPORO_EXAMPLE_DIR}"

# trap to stop services in case of error
trap 'docker compose down >/dev/null && echo "Test failed." && exit 1' ERR

# Function to start services
start_services() {
  echo "=== Starting NII-DG and Sapporo using docker compose ... ==="
  docker compose down >/dev/null
  docker compose up -d
  sleep 3
  echo "=== Checking if NII-DG and Sapporo are running ... ==="
  curl -sS localhost:5000/healthcheck >/dev/null
  curl -sS localhost:1122/healthcheck >/dev/null
}

# Function to run and monitor a workflow
run_workflow() {
  echo "=== Running a test workflow using Sapporo ... ==="
  run_id=$(python3 execute_workflow.py http://localhost:1122 | jq -r .run_id)
  echo "run_id: ${run_id}"
  sleep 3
  echo "=== Waiting for the workflow to complete ... ==="
  while true; do
    state=$(curl -sS "localhost:1122/runs/${run_id}/status" | jq -r .state)
    echo "state: ${state}"
    if [[ "${state}" == "COMPLETE" ]]; then
      break
    fi
    sleep 5
  done
  if [[ "${state}" != "COMPLETE" ]]; then
    echo "Workflow did not complete successfully."
    exit 1
  fi
}

# Function to process the results
process_results() {
  echo "=== Downloading the results of the workflow ... ==="
  rm -rf ./results
  mkdir -p ./results
  python3 download_results.py http://localhost:1122 "${run_id}" ./results
  ls -l ./results
  echo "=== Packaging the results of the workflow as RO-Crate ... ==="
  python3 package_ro_crate.py http://sapporo-service:1122 ./results
  ls -l ./ro-crate-metadata.json
  head ./ro-crate-metadata.json
}

# Function to validate the results
validate_results() {
  echo "=== Validating the RO-Crate using NII-DG API Server ... ==="
  request_id=$(curl -sS -X POST -H "Content-Type: application/json" -d @./ro-crate-metadata.json http://localhost:5000/validate | jq -r .request_id)
  echo "request_id: ${request_id}"
  echo "=== Waiting for the validation to complete ... ==="
  while true; do
    status=$(curl -sS "localhost:5000/${request_id}" | jq -r .status)
    echo "status: ${status}"
    if [[ "${status}" == "COMPLETE" ]]; then
      break
    fi
    sleep 5
  done
  if [[ "${status}" != "COMPLETE" ]]; then
    echo "Validation did not complete successfully."
    exit 1
  fi
  results=$(curl -sS "localhost:5000/${request_id}" | jq -r .results)
  echo "validation results (empty if succeeded): ${results}"
}

# Function to cleanup
cleanup() {
  echo "=== Stopping NII-DG and Sapporo using docker compose ... ==="
  docker compose down >/dev/null
  echo "=== Cleaning up ... ==="
  rm -rf ./results
  rm -f ./ro-crate-metadata.json
}

# Start services
start_services

# Run a test workflow
run_workflow

# Process the results
process_results

# Validate the results
validate_results

# Clean up
cleanup
