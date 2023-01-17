#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import Organization


def test_init() -> None:
    ent = Organization("https://ror.org/04ksd4g47")
    assert ent["@id"] == "https://ror.org/04ksd4g47"
    assert ent["@type"] == "Organization"
    assert ent.schema_name == "base"
    assert ent.entity_name == "Organization"


def test_as_jsonld() -> None:
    ent = Organization("https://ror.org/04ksd4g47")

    ent["name"] = "National Institute of Informatics"
    ent["alias"] = "NII"
    ent["description"] = "Japan's only general academic research institution seeking to create future value in the new discipline of informatics."

    jsonld = {'@type': 'Organization', '@id': 'https://ror.org/04ksd4g47', 'name': 'National Institute of Informatics', 'alias': 'NII',
              'description': "Japan's only general academic research institution seeking to create future value in the new discipline of informatics."}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = Organization("file:///config/setting.txt", {"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(PropsError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: type error
    ent["name"] = ["National Institute of Informatics"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: @id value is not relative path nor URL
    ent["name"] = "National Institute of Informatics"
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["@id"] = "https://ror.org/04ksd4g47"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
