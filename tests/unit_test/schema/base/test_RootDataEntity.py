#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.schema.base import Organization, RootDataEntity


def test_init() -> None:
    ent = RootDataEntity({})
    assert ent["@id"] == "./"
    assert ent["@type"] == "Dataset"
    assert ent.schema_name == "base"
    assert ent.entity_name == "RootDataEntity"


def test_as_jsonld() -> None:
    ent = RootDataEntity({})

    ent["name"] = "Example Research Project"
    ent["description"] = "This research project aims to reveal the effect of xxx."
    ent["funder"] = [Organization("https://ror.org/01b9y6c26")]
    ent["dateCreated"] = "2022-12-09T10:48:07.976+00:00"

    jsonld = {'@type': 'Dataset', '@id': './', 'name': 'Example Research Project', 'description': 'This research project aims to reveal the effect of xxx.',
              'funder': [{'@id': 'https://ror.org/01b9y6c26'}]}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"], ent_in_json["dateCreated"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = RootDataEntity({"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(EntityError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    ent["name"] = "Example Research Project"
    ent["funder"] = Organization("https://ror.org/01b9y6c26")
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    ent["funder"] = [Organization("https://ror.org/01b9y6c26")]
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
