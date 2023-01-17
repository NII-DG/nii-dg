#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.amed import ClinicalResearchRegistration


def test_init() -> None:
    ent = ClinicalResearchRegistration("https://jrct.niph.go.jp/latest-detail/jRCT202211111111")
    assert ent["@id"] == "https://jrct.niph.go.jp/latest-detail/jRCT202211111111"
    assert ent["@type"] == "ClinicalResearchRegistration"
    assert ent.schema_name == "amed"
    assert ent.entity_name == "ClinicalResearchRegistration"


def test_as_jsonld() -> None:
    ent = ClinicalResearchRegistration("https://jrct.niph.go.jp/latest-detail/jRCT202211111111")

    ent["name"] = "Japan Registry of Clinical Trials"
    ent["value"] = "1234567"

    jsonld = {'@type': 'ClinicalResearchRegistration', '@id': 'https://jrct.niph.go.jp/latest-detail/jRCT202211111111',
              'name': 'Japan Registry of Clinical Trials', 'value': '1234567'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = ClinicalResearchRegistration("file:///config/setting.txt", {"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(PropsError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: type error
    ent["name"] = "sample registration service"
    ent["value"] = 1
    with pytest.raises(PropsError):
        ent.check_props()

    # error: @id value is not URL
    ent["@id"] = "https://example.com"
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["value"] = "1"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
