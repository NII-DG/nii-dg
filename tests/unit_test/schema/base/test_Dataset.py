#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.schema.base import Dataset


def test_init() -> None:
    ent = Dataset("config/")
    assert ent["@id"] == "config/"
    assert ent["@type"] == "Dataset"
    assert ent.schema_name == "base"
    assert ent.entity_name == "Dataset"


def test_as_jsonld() -> None:
    ent = Dataset("config/")

    ent["name"] = "config"
    ent["url"] = "https://github.com/username/repository/directory"

    jsonld = {'@type': 'Dataset', '@id': 'config/', 'name': 'config', 'url': 'https://github.com/username/repository/directory'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = Dataset("file:///config/", {"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(EntityError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    ent["name"] = 12345
    with pytest.raises(EntityError):
        ent.check_props()

    # error: @id value is not relative path nor URL
    ent["name"] = "config"
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    ent["@id"] = "config/"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
