#!/usr/bin/env python3
# coding: utf-8

import pytest
from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Organization, Person


def test_init() -> None:
    ent = Person("https://orcid.org/0000-0001-2345-6789")
    assert ent["@id"] == "https://orcid.org/0000-0001-2345-6789"
    assert ent["@type"] == "Person"
    assert ent.schema_name == "base"
    assert ent.entity_name == "Person"


def test_as_jsonld() -> None:
    ent = Person("https://orcid.org/0000-0001-2345-6789")

    ent["name"] = "Ichiro Suzuki"
    ent["alias"] = "S. Ichiro"
    ent["affiliation"] = Organization("https://ror.org/04ksd4g47")
    ent["email"] = "ichiro@example.com"
    ent["telephone"] = "03-0000-0000"

    jsonld = {'@type': 'Person', '@id': 'https://orcid.org/0000-0001-2345-6789', 'name': 'Ichiro Suzuki', 'alias': 'S. Ichiro',
              'affiliation': {'@id': 'https://ror.org/04ksd4g47'}, 'email': 'ichiro@example.com', 'telephone': '03-0000-0000'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = Person("file:///config/setting.txt", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    # error: @id value is not URL
    ent["name"] = ["Ichiro Suzuki"]
    ent["email"] = "ichiro@example.com"
    with pytest.raises(EntityError):
        ent.check_props()

    # error: ORCID is invalid
    del ent["unknown_property"]
    ent["@id"] = "https://orcid.org/1234567891011128"
    ent["name"] = "Ichiro Suzuki"
    ent["affiliation"] = Organization("https://ror.org/04ksd4g47")
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    ent["@id"] = "https://orcid.org/1234-5678-9101-1128"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    person = Person("https://example.com/person")

    # error: not accessible URL
    with pytest.raises(EntityError):
        person.validate(crate)

    # no error occurs with accessible URL
    person["@id"] = "https://example.com"
    person.validate(crate)
