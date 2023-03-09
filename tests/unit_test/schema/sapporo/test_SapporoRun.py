#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset
from nii_dg.schema.sapporo import File, SapporoRun


def test_init() -> None:
    ent = SapporoRun()
    assert ent["@id"] == "#sapporo-run"
    assert ent["@type"] == "SapporoRun"
    assert ent.schema_name == "sapporo"
    assert ent.entity_name == "SapporoRun"


def test_as_jsonld() -> None:
    ent = SapporoRun()

    ent["run_request"] = File("run_request.json")
    ent["sapporo_config"] = File("sapporo_config.json")
    ent["state"] = "COMPLETE"
    ent["outputs"] = Dataset("outputs/", {"name": "outputs"})

    jsonld = {"@type": "SapporoRun", "@id": "#sapporo-run", "run_request": {"@id": "run_request.json"},
              "sapporo_config": {"@id": "sapporo_config.json"}, "state": "COMPLETE", "outputs": {"@id": "outputs/"}}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = SapporoRun(props={"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required property
    # error: type error
    ent["state"] = 100
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    del ent["unknown_property"]
    ent["run_request"] = File("run_request.json")
    ent["sapporo_config"] = File("sapporo_config.json")
    ent["state"] = "COMPLETE"
    ent["outputs"] = Dataset("outputs/", {"name": "outputs"})
    ent.check_props()


def test_validate() -> None:
    # to test this method, sapporo-service server is required
    pass
