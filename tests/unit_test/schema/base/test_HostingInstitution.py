#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import HostingInstitution


def test_init() -> None:
    ent = HostingInstitution("https://ror.org/04ksd4g47")
    assert ent["@id"] == "https://ror.org/04ksd4g47"
    assert ent["@type"] == "HostingInstitution"
    assert ent.schema_name == "base"
    assert ent.entity_name == "HostingInstitution"


def test_as_jsonld() -> None:
    ent = HostingInstitution("https://ror.org/04ksd4g47")

    ent["name"] = "National Institute of Informatics"
    ent["description"] = "Japan's only general academic research institution seeking to create future value in the new discipline of informatics."
    ent["address"] = "2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430"

    jsonld = {'@type': 'HostingInstitution', '@id': 'https://ror.org/04ksd4g47', 'name': 'National Institute of Informatics',
              'description': "Japan's only general academic research institution seeking to create future value in the new discipline of informatics.", 'address': '2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = HostingInstitution("file:///config/setting.txt", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    # error: @id value is not relative path nor URL
    ent["description"] = "Japan's only general academic research institution seeking to create future value in the new discipline of informatics."
    ent["address"] = ["2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430"]
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    del ent["unknown_property"]
    ent["name"] = "National Institute of Informatics"
    ent["address"] = "2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430"
    ent["@id"] = "https://ror.org/04ksd4g47"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    org = HostingInstitution("https://ror.org/04ksd4g47", {"name": "NII"})

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
