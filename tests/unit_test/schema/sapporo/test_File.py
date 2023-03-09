#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.sapporo import File, SapporoRun


def test_init() -> None:
    ent = File("run_request.json")
    assert ent["@id"] == "run_request.json"
    assert ent["@type"] == "File"
    assert ent.schema_name == "sapporo"
    assert ent.entity_name == "File"


def test_as_jsonld() -> None:
    ent = File("run_request.json")

    ent["contentSize"] = "1560B"
    ent["sha256"] = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    ent["contents"] = "test"

    jsonld = {"@type": "File", "@id": "run_request.json", "contentSize": "1560B",
              "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "contents": "test"}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = File("run_request.json", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: type error
    ent["contentSize"] = 1560
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    del ent["unknown_property"]
    ent["contentSize"] = "1560B"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    ent = File("run_request.json")

    # error: SapporoRun entity MUST be included in the crate
    with pytest.raises(EntityError):
        ent.validate(crate)

    # no error occurs
    run = SapporoRun()
    crate.add(run)
    ent.validate(crate)
