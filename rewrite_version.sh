#!/usr/bin/env bash

# This script updates the version number of the NII-DG library across multiple files.
# Usage: ./<scriptname> <new_version>

set -euo pipefail

# Ensure the new version number is provided as an argument
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <new_version>"
  exit 1
fi

PREV_VERSION=$(python3 ./nii_dg/module_info.py)
NEW_VERSION=$1

read -p "Rewrite version from ${PREV_VERSION} to ${NEW_VERSION}? (y/n) :" YN

if [[ "${YN}" != "y" ]]; then
  echo "Abort."
  exit 1
fi

echo "Rewriting version from ${PREV_VERSION} to ${NEW_VERSION} ..."

echo "Rewriting nii_dg/module_info.py ..."
sed -i "s/GH_REF: str = \"${PREV_VERSION}\"/GH_REF: str = \"${NEW_VERSION}\"/g" ./nii_dg/module_info.py

echo "Rewriting Dockerfile ..."
sed -i "s/LABEL org.opencontainers.image.version=\"${PREV_VERSION}\"/LABEL org.opencontainers.image.version=\"${NEW_VERSION}\"/g" ./Dockerfile

echo "Rewriting compose.yml ..."
sed -i "s/image: ghcr.io\/nii-dg\/nii-dg:${PREV_VERSION}/image: ghcr.io\/nii-dg\/nii-dg:${NEW_VERSION}/g" ./compose.yml

echo "Rewriting compose.api.yml ..."
sed -i "s/image: ghcr.io\/nii-dg\/nii-dg:${PREV_VERSION}/image: ghcr.io\/nii-dg\/nii-dg:${NEW_VERSION}/g" ./compose.api.yml

echo "Version update complete."
