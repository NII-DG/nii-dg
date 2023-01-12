#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
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
    with pytest.raises(PropsError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: type error
    ent["name"] = "National Institute of Informatics"
    ent["description"] = "Japan's only general academic research institution seeking to create future value in the new discipline of informatics."
    ent["address"] = ["2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: @id value is not relative path nor URL
    ent["address"] = "2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430"
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["@id"] = "https://ror.org/04ksd4g47"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
