#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Organization
from nii_dg.schema.cao import Person


def test_init() -> None:
    ent = Person("https://orcid.org/0000-0001-2345-6789")
    assert ent["@id"] == "https://orcid.org/0000-0001-2345-6789"
    assert ent["@type"] == "Person"
    assert ent.schema_name == "cao"
    assert ent.entity_name == "Person"


def test_as_jsonld() -> None:
    ent = Person("https://orcid.org/0000-0001-2345-6789")

    ent["name"] = "Ichiro Suzuki"
    ent["alias"] = "S. Ichiro"
    ent["affiliation"] = Organization("https://ror.org/04ksd4g47")
    ent["email"] = "ichiro@example.com"
    ent["telephone"] = "03-0000-0000"
    ent["eradResearcherNumber"] = "01234567"

    jsonld = {'@type': 'Person', '@id': 'https://orcid.org/0000-0001-2345-6789', 'name': 'Ichiro Suzuki', 'alias': 'S. Ichiro',
              'affiliation': {'@id': 'https://ror.org/04ksd4g47'}, 'email': 'ichiro@example.com', 'telephone': '03-0000-0000', 'eradResearcherNumber': '01234567'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = Person("file:///config/setting.txt", {"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(EntityError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    ent["name"] = "Ichiro Suzuki"
    ent["alias"] = "S. Ichiro"
    ent["affiliation"] = Organization("https://ror.org/04ksd4g47")
    ent["email"] = "ichiro@example.com"
    ent["telephone"] = "03-0000-0000"
    ent["eradResearcherNumber"] = 1234567
    with pytest.raises(EntityError):
        ent.check_props()

    # error: @id value is not URL
    ent["eradResearcherNumber"] = "01234567"
    with pytest.raises(EntityError):
        ent.check_props()

    # error: ORCID is invalid
    ent["@id"] = "https://orcid.org/1234567891011128"
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    ent["@id"] = "https://orcid.org/1234-5678-9101-1128"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    ent = Person("https://example.com/person")
    crate.add(ent)

    # error: not accessible URL
    with pytest.raises(EntityError):
        ent.validate(crate)

    # no error occurs with accessible URL
    ent["@id"] = "https://example.com"
    ent.validate(crate)
