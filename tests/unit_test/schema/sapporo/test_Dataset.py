#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.sapporo import Dataset, File, SapporoRun


def test_init() -> None:
    ent = Dataset("outputs/")
    assert ent["@id"] == "outputs/"
    assert ent["@type"] == "Dataset"
    assert ent.schema_name == "sapporo"
    assert ent.entity_name == "Dataset"


def test_as_jsonld() -> None:
    ent = Dataset("outputs/")

    ent["name"] = "outputs"
    ent["hasPart"] = [File("outputs/file_1.txt", {"name": "file_1.txt"})]

    jsonld = {"@type": "Dataset", "@id": "outputs/", "name": "outputs", "hasPart": [{"@id": "outputs/file_1.txt"}]}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = Dataset("file:///outputs/", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: @id value is not relative path nor URL
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    del ent["unknown_property"]
    ent["@id"] = "outputs/"
    ent["name"] = 12345
    ent["hasPart"] = [File("outputs/file_1.txt", {"name": "file_1.txt"})]
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    ent["name"] = "outputs"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    ent = Dataset("outputs/", {"hasPart": [{"@id": "outputs/file_1.txt"}]})

    # error: SapporoRun entity MUST be included in the crate
    # error: Entity in hasPart property not included in the crate
    with pytest.raises(EntityError):
        ent.validate(crate)

    # no error occurs
    run = SapporoRun()
    file = File("outputs/file_1.txt")
    crate.add(run, file)
    ent.validate(crate)
