#!/usr/bin/env python3
# coding: utf-8

import importlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import nii_dg
from nii_dg.error import CrateCheckPropsError, CrateValidationError, EntityError
from nii_dg.ro_crate import ROCrate

here = Path(__file__).parent.resolve()

sample_crate_jsonld_path = here.joinpath("../example/sample_crate.json").resolve()
invalid_crate1_jsonld_path = here.joinpath("../example/invalid_crate1.json").resolve()
invalid_crate2_jsonld_path = here.joinpath("../example/invalid_crate2.json").resolve()


@pytest.mark.parametrize("use_external_ctx", [True, False])
def test_validate_valid_crate(use_external_ctx: bool) -> None:
    with sample_crate_jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    with patch("os.environ", {"DG_USE_EXTERNAL_CTX": str(use_external_ctx)}):
        importlib.reload(nii_dg.utils)
        importlib.reload(nii_dg.ro_crate)

        ro_crate = ROCrate(jsonld=jsonld)
        ro_crate.check_props()
        ro_crate.validate()


@pytest.mark.parametrize("use_external_ctx", [True, False])
def test_validate_invalid_crate1(use_external_ctx: bool) -> None:
    with invalid_crate1_jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    with patch("os.environ", {"DG_USE_EXTERNAL_CTX": str(use_external_ctx)}):
        importlib.reload(nii_dg.utils)
        importlib.reload(nii_dg.ro_crate)

        ro_crate = ROCrate(jsonld=jsonld)
        with pytest.raises(CrateValidationError) as e:
            ro_crate.check_props()
            ro_crate.validate()

        for error in e.value.errors:
            assert isinstance(error, EntityError)


@pytest.mark.parametrize("use_external_ctx", [True, False])
def test_validate_invalid_crate2(use_external_ctx: bool) -> None:
    with invalid_crate2_jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    with patch("os.environ", {"DG_USE_EXTERNAL_CTX": str(use_external_ctx)}):
        importlib.reload(nii_dg.utils)
        importlib.reload(nii_dg.ro_crate)

        ro_crate = ROCrate(jsonld=jsonld)
        with pytest.raises(CrateCheckPropsError) as e:
            ro_crate.check_props()
            ro_crate.validate()

        for error in e.value.errors:
            assert isinstance(error, EntityError)
