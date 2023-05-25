#!/usr/bin/env python3
# coding: utf-8

import json
from pathlib import Path

import pytest

from nii_dg.error import (CrateCheckPropsError, CrateValidationError,
                          EntityError)
from nii_dg.ro_crate import ROCrate

here = Path(__file__).parent.resolve()

sample_crate_jsonld_path = here.joinpath("../example/sample_crate.json").resolve()
invalid_crate1_jsonld_path = here.joinpath("../example/invalid_crate1.json").resolve()
invalid_crate2_jsonld_path = here.joinpath("../example/invalid_crate2.json").resolve()


def test_validate_valid_crate() -> None:
    with sample_crate_jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    ro_crate = ROCrate(jsonld=jsonld)
    ro_crate.validate()


def test_validate_invalid_crate1() -> None:
    with invalid_crate1_jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    ro_crate = ROCrate(jsonld=jsonld)
    with pytest.raises(CrateValidationError) as e:
        ro_crate.check_props()
        ro_crate.validate()

    for error in e.value.errors:
        assert isinstance(error, EntityError)


def test_validate_invalid_crate2() -> None:
    with invalid_crate2_jsonld_path.open("r", encoding="utf-8") as f:
        jsonld = json.load(f)
    ro_crate = ROCrate(jsonld=jsonld)
    with pytest.raises(CrateCheckPropsError) as e:
        ro_crate.check_props()
        ro_crate.validate()

    for error in e.value.errors:
        assert isinstance(error, EntityError)
