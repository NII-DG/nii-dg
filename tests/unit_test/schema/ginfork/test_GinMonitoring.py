#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset, RootDataEntity
from nii_dg.schema.ginfork import File, GinMonitoring


def test_init() -> None:
    ent = GinMonitoring(1)
    assert ent["@id"] == "#ginmonitoring:1"
    assert ent["@type"] == "GinMonitoring"
    assert ent.schema_name == "ginfork"
    assert ent.entity_name == "GinMonitoring"


def test_as_jsonld() -> None:
    ent = GinMonitoring(1)

    ent["about"] = RootDataEntity({})
    ent["contentSize"] = "100GB"
    ent["workflowIdentifier"] = "bio"
    ent["datasetStructure"] = "with_code"

    jsonld = {'@type': 'GinMonitoring', '@id': '#ginmonitoring:1', 'about': {'@id': './'},
              'contentSize': '100GB', 'workflowIdentifier': 'bio', 'datasetStructure': 'with_code'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = GinMonitoring(1, {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    ent["contentSize"] = "10GB"
    ent["workflowIdentifier"] = "basic"
    ent["datasetStructure"] = "basic"
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    del ent["unknown_property"]
    ent["about"] = RootDataEntity()
    ent["datasetStructure"] = "with_code"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()

    ent = GinMonitoring(1)
    ent["about"] = RootDataEntity()
    ent["contentSize"] = "10GB"
    ent["workflowIdentifier"] = "basic"
    ent["datasetStructure"] = "with_code"

    file = File("test/file")
    file["contentSize"] = "15GB"
    file["experimentPackageFlag"] = True
    crate.add(file, ent)

    # error: over filesize
    # error: about property is unrelated
    # error: specific named directories are missing; source, input_data and output_data
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["about"] = crate.root
    file["contentSize"] = "9GB"
    dir_1 = Dataset("source/", {"name": "source"})
    dir_2 = Dataset("input_data/", {"name": "input_data"})
    dir_3 = Dataset("root/output_data/", {"name": "output_data"})
    crate.add(dir_1, dir_2, dir_3)

    # error: specific named directories are not in the same level
    with pytest.raises(EntityError):
        ent.validate(crate)

    dir_3["@id"] = "output_data/"
    # no error occurred
    ent.validate(crate)
