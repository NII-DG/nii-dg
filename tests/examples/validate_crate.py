#!/usr/bin/env python3
# coding: utf-8

import json
import sys
from pathlib import Path

from nii_dg.ro_crate import ROCrate


def validate_crate(crate: ROCrate) -> None:
    crate.validate()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python load_crate.py <crate.json>")
        sys.exit(1)

    jsonld_path = Path(sys.argv[1]).resolve()
    with jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)

    crate = ROCrate(jsonld=jsonld)

    validate_crate(crate)


if __name__ == "__main__":
    main()
