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


def test_schema() -> None:
    ent = DMP(1)
    assert ent.schema == "amed"


def test_check_props() -> None:
    ent = DMP(1)

    # error
    with pytest.raises(PropsError) as e1:
        ent.check_props()
    assert str(e1.value) == "The term name is required in <DMP #dmp:1>."

    with pytest.raises(PropsError) as e2:
        ent["name"] = "test"
        ent.check_props()
    assert str(e2.value) == "The term description is required in <DMP #dmp:1>."

    with pytest.raises(PropsError) as e3:
        ent["description"] = "sample project"
        ent.check_props()
    assert str(e3.value) == "The term keyword is required in <DMP #dmp:1>."

    with pytest.raises(PropsError) as e4:
        ent["keyword"] = "Informatics"
        ent.check_props()
    assert str(e4.value) == "The term accessRights is required in <DMP #dmp:1>."

    with pytest.raises(PropsError) as e5:
        ent["accessRights"] = "open access"
        ent.check_props()
    assert str(e5.value) == "The term gotInformedConsent is required in <DMP #dmp:1>."

    with pytest.raises(PropsError) as e6:
        ent["gotInformedConsent"] = "got"
        ent.check_props()
    assert str(e6.value) == "The the value of accessRights in <DMP #dmp:1> MUST be one of ('Unshared', 'Restricted Closed Sharing', 'Restricted Open Sharing', 'Unrestricted Open Sharing'); got open access instead."

    with pytest.raises(PropsError) as e7:
        ent["accessRights"] = "Unshared"
        ent.check_props()
    assert str(e7.value) == "The the value of gotInformedConsent in <DMP #dmp:1> MUST be one of ('yes', 'no', 'unknown'); got got instead."


def test_as_jsonld() -> None:
    ent = DMP(1, {
        "name": "test dataset",
        "description": "brabra",
        "keyword": "Informatics",
        "accessRights": "Unshared",
        "availabilityStarts": "2023-04-01",
        "accessRightsInfo": "Because dataset includes personal information",
        "contentSize": "1GB",
        "gotInformedConsent": "yes",
        "informedConsentFormat": "AMED"
    })
    ent["repository"] = RepositoryObject("https://example.com/repository")
    ent["distribution"] = DataDownload("https://example.com/datadownload")
    ent["identifier"] = [ClinicalResearchRegistration("https://example.com/jrct")]

    jsonld = {
        "@id": "#dmp:1",
        "@type": "DMP",
        "name": "test dataset",
        "description": "brabra",
        "keyword": "Informatics",
        "accessRights": "Unshared",
        "availabilityStarts": "2023-04-01",
        "accessRightsInfo": "Because dataset includes personal information",
        "repository": {"@id": "https://example.com/repository"},
        "distribution": {"@id": "https://example.com/datadownload"},
        "contentSize": "1GB",
        "gotInformedConsent": "yes",
        "informedConsentFormat": "AMED",
        "identifier": [{"@id": "https://example.com/jrct"}],
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/amed/DMP.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
