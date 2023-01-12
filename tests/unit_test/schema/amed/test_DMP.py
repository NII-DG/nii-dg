#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.amed import DMP, ClinicalResearchRegistration
from nii_dg.schema.base import DataDownload, RepositoryObject


def test_init() -> None:
    ent = DMP(1)
    assert ent["@id"] == "#dmp:1"
    assert ent["@type"] == "DMP"
    assert ent.schema_name == "amed"
    assert ent.entity_name == "DMP"


def test_as_jsonld() -> None:
    ent = DMP(1)

    ent["name"] = "calculated data"
    ent["description"] = "Result data calculated by Newton's method"
    ent["keyword"] = "biological origin data"
    ent["accessRights"] = "Unrestricted Open Sharing"
    ent["availabilityStarts"] = "9999-04-01"
    ent["accessRightsInfo"] = "Because the dataset contains personal information."
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["contentSize"] = "100GB"
    ent["gotInformedConsent"] = "yes"
    ent["informedConsentFormat"] = "AMED"
    ent["identifier"] = [ClinicalResearchRegistration("https://jrct.niph.go.jp/latest-detail/jRCT202211111111")]

    jsonld = {'@type': 'DMP', '@id': '#dmp:1', 'name': 'calculated data', 'description': "Result data calculated by Newton's method", 'keyword': 'biological origin data', 'accessRights': 'Unrestricted Open Sharing', 'availabilityStarts': '9999-04-01', 'accessRightsInfo': 'Because the dataset contains personal information.',
              'repository': {'@id': 'https://doi.org/xxxxxxxx'}, 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'contentSize': '100GB', 'gotInformedConsent': 'yes', 'informedConsentFormat': 'AMED', 'identifier': [{'@id': 'https://jrct.niph.go.jp/latest-detail/jRCT202211111111'}]}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = DMP(1, {"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(PropsError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: type error
    ent["name"] = "calculated data"
    ent["description"] = "Result data calculated by Newton's method"
    ent["keyword"] = "biological origin data"
    ent["accessRights"] = "Unrestricted Open Sharing"
    ent["availabilityStarts"] = 2022
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["gotInformedConsent"] = "yes"
    ent["informedConsentFormat"] = "AMED"
    with pytest.raises(PropsError):
        ent.check_props()

    # error: availabilityStarts value is not future date
    ent["availabilityStarts"] = "2022-04-01"
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["availabilityStarts"] = "9999-04-01"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
