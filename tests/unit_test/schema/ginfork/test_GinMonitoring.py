#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.schema.ginfork import GinMonitoring

from nii_dg.schema.base import RootDataEntity


def test_init() -> None:
    ent = GinMonitoring(1)
    assert ent["@id"] == "#ginmonitoring:1"
    assert ent["@type"] == "GinMonitoring"
    assert ent.schema_name == "ginfork"
    assert ent.entity_name == "GinMonitoring"


def test_as_jsonld() -> None:
    ent = GinMonitoring(1)

    ent["about"] = RootDataEntity("./")
    ent["contentSize"] = "100GB"
    ent["workflowIdentifier"] = "bio"
    ent["datasetStructure"] = "bio"

    jsonld = {'@type': 'GinMonitoring', '@id': '#ginmonitoring:1', 'about': {'@id': './'}, 'contentSize': '100GB', 'workflowIdentifier': 'bio', 'datasetStructure': 'bio'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    # TO BE UPDATED
    pass


def test_validate() -> None:
    # TO BE UPDATED
    pass
