#!/usr/bin/env python3
# coding: utf-8

import json
from pathlib import Path

import pytest

from nii_dg.ro_crate import ROCrate

here = Path(__file__).parent.resolve()

sample_crate_jsonld_path = here.joinpath("../example/sample_crate.json").resolve()
invalid_crate1_jsonld_path = here.joinpath("../example/invalid_crate1.json").resolve()
invalid_crate2_jsonld_path = here.joinpath("../example/invalid_crate2.json").resolve()


@pytest.mark.parametrize("jsonld_path", [sample_crate_jsonld_path, invalid_crate1_jsonld_path, invalid_crate2_jsonld_path])
def test_load_crate(jsonld_path: Path) -> None:
    with jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    ROCrate(jsonld=jsonld)
