#!/usr/bin/env bash

# This script updates the version number of the NII-DG library across multiple files.
# Usage: ./<scriptname> <new_version>

set -euo pipefail

# Ensure the new version number is provided as an argument
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <new_version>"
  exit 1
fi

NEW_VERSION=$1

# Define the locations and current version patterns to replace
declare -A LOCATIONS=(
  ["./nii_dg/module_info.py"]="GH_REF: str = \"[0-9]*\.[0-9]*\.[0-9]*\""
  ["./Dockerfile"]="LABEL org.opencontainers.image.version=\"[0-9]*\.[0-9]*\.[0-9]*\""
  ["./compose.yml"]="image: ghcr.io\/nii-dg\/nii-dg:[0-9]*\.[0-9]*\.[0-9]*"
  ["./compose.api.yml"]="image: ghcr.io\/nii-dg\/nii-dg:[0-9]*\.[0-9]*\.[0-9]*"
)

# Iterate over the locations and update the version
for FILE in "${!LOCATIONS[@]}"; do
  PATTERN=${LOCATIONS[$FILE]}
  echo "Updating version in $FILE ..."
  sed -i -r "s/${PATTERN}/${PATTERN%%[0-9]*\.[0-9]*\.[0-9]*\"}${NEW_VERSION}\"/g" $FILE
done

echo "Version update complete."
