#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.schema.base import RootDataEntity
from nii_dg.schema.ginfork import GinMonitoring


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
    with pytest.raises(EntityError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    ent["about"] = RootDataEntity()
    ent["contentSize"] = "10GB"
    ent["workflowIdentifier"] = "basic"
    ent["datasetStructure"] = "basic"
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    ent["datasetStructure"] = "with_code"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
