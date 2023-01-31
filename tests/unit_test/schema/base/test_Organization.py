#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
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
    # error: lack of required properties
    # error: @id value is not relative path nor URL
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    del ent["unknown_property"]
    ent["@id"] = "https://ror.org/04ksd4g47"
    ent["name"] = ["National Institute of Informatics"]
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    ent["name"] = "National Institute of Informatics"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    org = Organization("https://ror.org/04ksd4g47", {"name": "NII"})

    # error: name is not the same as the name registered in ROR
    with pytest.raises(EntityError):
        org.validate(crate)

    # no error occurs with registered name
    org["name"] = "National Institute of Informatics"
    org.validate(crate)

    org["@id"] = "https://example.com/organization"
    # error: not accessible URL
    with pytest.raises(EntityError):
        org.validate(crate)

    # no error occurs with accessible URL
    org["@id"] = "https://example.com"
    org.validate(crate)
