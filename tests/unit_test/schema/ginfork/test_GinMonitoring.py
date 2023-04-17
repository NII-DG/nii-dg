#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.entity import RootDataEntity
from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset
from nii_dg.schema.ginfork import File, GinMonitoring


def test_init() -> None:
    ent = GinMonitoring()
    assert ent["@id"] == "#ginmonitoring"
    assert ent["@type"] == "GinMonitoring"
    assert ent.schema_name == "ginfork"
    assert ent.entity_name == "GinMonitoring"


def test_as_jsonld() -> None:
    ent = GinMonitoring()

    ent["about"] = RootDataEntity({})
    ent["contentSize"] = "100GB"
    ent["workflowIdentifier"] = "bio"
    ent["datasetStructure"] = "with_code"
    ent["experimentPackageList"] = ["experiments/exp1/"]

    jsonld = {"@type": "GinMonitoring", "@id": "#ginmonitoring", "about": {"@id": "./"}, "contentSize": "100GB",
              "workflowIdentifier": "bio", "datasetStructure": "with_code", "experimentPackageList": ["experiments/exp1/"]}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = GinMonitoring("#ginmonitoring", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    ent["contentSize"] = "10GB"
    ent["workflowIdentifier"] = "basic"
    ent["datasetStructure"] = "basic"
    ent["experimentPackageList"] = ["experiments/exp1/"]
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    del ent["unknown_property"]
    ent["about"] = RootDataEntity()
    ent["datasetStructure"] = "with_code"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()

    ent = GinMonitoring()
    ent["about"] = RootDataEntity()
    ent["contentSize"] = "10GB"
    ent["workflowIdentifier"] = "basic"
    ent["datasetStructure"] = "with_code"
    ent["experimentPackageList"] = ["experiments/exp1/"]

    file = File("experiments/exp1/source/test.txt")
    file["contentSize"] = "15GB"
    file["experimentPackageFlag"] = True
    dir_1 = Dataset("experiments/exp1/source/", {"name": "source"})
    crate.add(file, ent, dir_1)

    # error: over filesize
    # error: about property is unrelated
    # error: specific named directories are missing; experiments/exp1/input_data and experiments/exp1/output_data
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["about"] = {"@id": "./"}
    file["contentSize"] = "9GB"
    dir_2 = Dataset("experiments/exp1/input_data/", {"name": "input_data"})
    dir_3 = Dataset("experiments/exp1/output_data/", {"name": "output_data"})
    crate.add(dir_2, dir_3)

    # no error occurred
    ent.validate(crate)

    ent["datasetStructure"] = "for_parameters"
    # error: "parameterExperimentList" is required
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["parameterExperimentList"] = ["experiments/exp1/parameter/"]
    dir_3["@id"] = "experiments/exp1/parameter/output_data/"
    # error: "experiments/exp1/parameter/params/" is missing
    with pytest.raises(EntityError):
        ent.validate(crate)

    dir_4 = Dataset("experiments/exp1/parameter/params/", {"name": "params"})
    crate.add(dir_4)

    # no error occurred
    ent.validate(crate)
