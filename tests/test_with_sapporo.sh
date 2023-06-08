#!/usr/bin/env bash

# test_with_sapporo.sh
#
# This script is for testing with Sapporo.
# This script refers to `<root_dir>/sapporo_example.`
# This script is expected to be run on a host machine with Docker installed, and uses docker compose to start NII-DG and Sapporo.
#
# Required:
#   - docker
#   - docker compose
#   - python3 (with NII-DG library)
#   - jq
#   - curl

# Catch errors and stop NII-DG and Sapporo using docker compose.
# Then exit with an error message and code.
trap 'docker compose down >/dev/null && echo "Test failed." && exit 1' ERR

set -euxo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "${HERE}/.." && pwd)
SAPPORO_EXAMPLE_DIR="${ROOT_DIR}/sapporo_example"

cd "${SAPPORO_EXAMPLE_DIR}"

# Start NII-DG and Sapporo using docker compose.
echo "=== Starting NII-DG and Sapporo using docker compose ... ==="
docker compose down >/dev/null
docker compose up -d --build

# Wait for NII-DG and Sapporo to start.
echo "=== Waiting for NII-DG and Sapporo to start ... ==="
sleep 3

# Check if NII-DG and Sapporo are running. (silently)
echo "=== Checking if NII-DG and Sapporo are running ... ==="
curl -sS localhost:5000/healthcheck >/dev/null
curl -sS localhost:1122/healthcheck >/dev/null

# Run a test workflow using Sapporo.
echo "=== Running a test workflow using Sapporo ... ==="
run_id=$(python3 execute_workflow.py http://localhost:1122 | jq -r .run_id)
echo "run_id: ${run_id}"

sleep 3

# Wait for the workflow to complete.
echo "=== Waiting for the workflow to complete ... ==="
while true; do
  state=$(curl -sS "localhost:1122/runs/${run_id}/status" | jq -r .state)
  echo "state: ${state}"
  if [[ "${state}" == "COMPLETE" ]]; then
    break
  fi
  sleep 5
done

# Check if the workflow completed successfully.
if [[ "${state}" != "COMPLETE" ]]; then
  echo "Workflow did not complete successfully."
  exit 1
fi

# Download the results of the workflow.
echo "=== Downloading the results of the workflow ... ==="
rm -rf ./results
mkdir -p ./results
python3 download_results.py http://localhost:1122 "${run_id}" ./results
ls -l ./results

# Package the results of the workflow as RO-Crate.
echo "=== Packaging the results of the workflow as RO-Crate ... ==="
python3 package_ro_crate.py http://localhost:1122 ./results
ls -l ./ro-crate-metadata.json
head ./ro-crate-metadata.json

# Validate the RO-Crate using NII-DG API Server.
echo "=== Validating the RO-Crate using NII-DG API Server ... ==="
request_id=$(curl -sS -X POST -H "Content-Type: application/json" -d @./ro-crate-metadata.json http://localhost:5000/validate | jq .request_id)
echo "request_id: ${request_id}"

# Wait for the validation to complete.
echo "=== Waiting for the validation to complete ... ==="
while true; do
  status=$(curl -sS localhost:5000/"${request_id}" | jq -r .status)
  echo "status: ${status}"
  if [[ "${status}" == "COMPLETE" ]]; then
    break
  fi
  sleep 5
done

# Check if the validation completed successfully.
if [[ "${status}" != "COMPLETE" ]]; then
  echo "Validation did not complete successfully."
  exit 1
fi

# Check if the validation succeeded.
results=$(curl -sS localhost:5000/"${request_id}" | jq -r .results)
echo "validation results (empty if succeeded): ${results}"

# Stop NII-DG and Sapporo using docker compose.
echo "=== Stopping NII-DG and Sapporo using docker compose ... ==="
docker compose down >/dev/null

# Clean up.
echo "=== Cleaning up ... ==="
rm -rf ./results
rm -f ./ro-crate-metadata.json
