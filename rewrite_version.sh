#!/usr/bin/env bash

# rewrite version in:
#
# - nii_dg/module_info.py
#    - `GH_REF: str = "0.1.0"`
# - docs/conf.py
#    - `version = '0.1.0'`
#    - `release = '0.1.0'`
# - Dockerfile
#    - `LABEL org.opencontainers.image.version="0.1.0"`
# - compose.yml
#    - `image: ghcr.io/nii-dg/nii-dg:0.1.0`
# - compose.api.yml
#    - `image: ghcr.io/nii-dg/nii-dg:0.1.0`

set -euxo pipefail

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

echo "Rewriting docs/conf.py ..."
sed -i "s/version = '${PREV_VERSION}'/version = '${NEW_VERSION}'/g" ./docs/conf.py
sed -i "s/release = '${PREV_VERSION}'/release = '${NEW_VERSION}'/g" ./docs/conf.py

echo "Rewriting Dockerfile ..."
sed -i "s/LABEL org.opencontainers.image.version=\"${PREV_VERSION}\"/LABEL org.opencontainers.image.version=\"${NEW_VERSION}\"/g" ./Dockerfile

echo "Rewriting compose.yml ..."
sed -i "s/image: ghcr.io\/nii-dg\/nii-dg:${PREV_VERSION}/image: ghcr.io\/nii-dg\/nii-dg:${NEW_VERSION}/g" ./compose.yml

echo "Rewriting compose.api.yml ..."
sed -i "s/image: ghcr.io\/nii-dg\/nii-dg:${PREV_VERSION}/image: ghcr.io\/nii-dg\/nii-dg:${NEW_VERSION}/g" ./compose.api.yml

echo "Done."

exit 0
