#!/usr/bin/env python3
# coding: utf-8

import json
import sys
from pathlib import Path
from pprint import pprint

from nii_dg.ro_crate import ROCrate


def main(jsonld_path: Path) -> None:
    with jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    crate = ROCrate(jsonld=jsonld)
    print("=== Root ===")
    pprint(crate.root)
    print("=== Default ===")
    pprint(crate.default_entities)
    print("=== Data ===")
    pprint(crate.data_entities)
    print("=== Contextual ===")
    pprint(crate.contextual_entities)


if __name__ == "__main__":
    jsonld_path = Path(__file__).parent.joinpath(sys.argv[1])
    main(jsonld_path)
