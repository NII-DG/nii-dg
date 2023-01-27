#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import License


def test_init() -> None:
    ent = License("https://www.apache.org/licenses/LICENSE-2.0")
    assert ent["@id"] == "https://www.apache.org/licenses/LICENSE-2.0"
    assert ent["@type"] == "License"
    assert ent.schema_name == "base"
    assert ent.entity_name == "License"


def test_as_jsonld() -> None:
    ent = License("https://www.apache.org/licenses/LICENSE-2.0")

    ent["name"] = "Apache License 2.0"
    ent["description"] = "the licensed defined by Apache Software Foundation"

    jsonld = {'@type': 'License', '@id': 'https://www.apache.org/licenses/LICENSE-2.0',
              'name': 'Apache License 2.0', 'description': 'the licensed defined by Apache Software Foundation'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = License("file:///config/setting.txt", {"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(PropsError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: type error
    ent["name"] = ["Apache License 2.0"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: @id value is not relative path nor URL
    ent["name"] = "Apache License 2.0"
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["@id"] = "https://www.apache.org/licenses/LICENSE-2.0"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    lic = License("https://example.com/license")

    # error: not accessible URL
    with pytest.raises(EntityError):
        lic.validate(crate)

    # no error occurs with accessible URL
    lic["@id"] = "https://example.com"
    lic.validate(crate)
