#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import ContactPoint


def test_init() -> None:
    ent = ContactPoint("#mailto:contact@example.com")
    assert ent["@id"] == "#mailto:contact@example.com"
    assert ent["@type"] == "ContactPoint"
    assert ent.schema_name == "base"
    assert ent.entity_name == "ContactPoint"


def test_as_jsonld() -> None:
    ent = ContactPoint("#mailto:contact@example.com")

    ent["name"] = "Sample Inc., Open-Science department, data management unit"
    ent["email"] = "contact@example.com"
    ent["telephone"] = "03-0000-0000"

    jsonld = {'@type': 'ContactPoint', '@id': '#mailto:contact@example.com',
              'name': 'Sample Inc., Open-Science department, data management unit', 'email': 'contact@example.com', 'telephone': '03-0000-0000'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = ContactPoint("#mailto:test@example.com", {"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(EntityError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    ent["name"] = "Sample Inc., Open-Science department, data management unit"
    ent["email"] = ".test@example.com"
    ent["telephone"] = 12345678901
    with pytest.raises(EntityError):
        ent.check_props()

    # error: email is invalid
    ent["telephone"] = "03-0000-0000"
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    ent["email"] = "test@example.com"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    contact = ContactPoint("#mailto:test@example.com")

    # error: email is required
    with pytest.raises(EntityError):
        contact.validate(crate)

    contact["email"] = "notmatch@example.com"
    # error: email is not the same as @id
    with pytest.raises(EntityError):
        contact.validate(crate)

    contact["email"] = "test@example.com"
    # no error occurs
    contact.validate(crate)

    contact["@id"] = "#callto:09012345678"
    # error: telephone is required
    with pytest.raises(EntityError):
        contact.validate(crate)

    contact["telephone"] = "08012345678"
    # error: telephone is not the same as @id
    with pytest.raises(EntityError):
        contact.validate(crate)

    contact["telephone"] = "09012345678"
    # no error occurs
    contact.validate(crate)
