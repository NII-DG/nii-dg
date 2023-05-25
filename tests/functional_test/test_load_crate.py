#!/usr/bin/env python3
# coding: utf-8

import importlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import nii_dg
from nii_dg.ro_crate import ROCrate

here = Path(__file__).parent.resolve()

sample_crate_jsonld_path = here.joinpath("../example/sample_crate.json").resolve()
invalid_crate1_jsonld_path = here.joinpath("../example/invalid_crate1.json").resolve()
invalid_crate2_jsonld_path = here.joinpath("../example/invalid_crate2.json").resolve()

test_cases = [(jsonld_path, use_external_ctx)
              for jsonld_path in [sample_crate_jsonld_path, invalid_crate1_jsonld_path, invalid_crate2_jsonld_path]
              for use_external_ctx in [True]
              ]


@pytest.mark.parametrize("jsonld_path, use_external_ctx", test_cases)
def test_load_crate(jsonld_path: Path, use_external_ctx: bool) -> None:
    with jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    with patch("os.environ", {"DG_USE_EXTERNAL_CTX": str(use_external_ctx)}):
        importlib.reload(nii_dg.utils)
        importlib.reload(nii_dg.ro_crate)

        ROCrate(jsonld=jsonld)
