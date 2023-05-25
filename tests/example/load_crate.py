#!/usr/bin/env python3
# coding: utf-8

import json
import sys
from pathlib import Path
from pprint import pprint
from typing import Any, Dict

from nii_dg.ro_crate import ROCrate


def load_crate(jsonld: Dict[str, Any]) -> ROCrate:
    return ROCrate(jsonld=jsonld)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python load_crate.py <crate.json>")
        sys.exit(1)

    jsonld_path = Path(sys.argv[1]).resolve()
    with jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)

    ro_crate = load_crate(jsonld)

    print("=== Root ===")
    pprint(ro_crate.root)
    print("=== Default ===")
    pprint(ro_crate.default_entities)
    print("=== Data ===")
    pprint(ro_crate.data_entities)
    print("=== Contextual ===")
    pprint(ro_crate.contextual_entities)


if __name__ == "__main__":
    main()
