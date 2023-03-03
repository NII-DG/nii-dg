#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.amed import (DMP, ClinicalResearchRegistration, DMPMetadata,
                                File)
from nii_dg.schema.base import DataDownload, RepositoryObject


def test_init() -> None:
    ent = DMP("#dmp:1")
    assert ent["@id"] == "#dmp:1"
    assert ent["@type"] == "DMP"
    assert ent.schema_name == "amed"
    assert ent.entity_name == "DMP"


def test_as_jsonld() -> None:
    ent = DMP("#dmp:1")

    ent["dataNumber"] = 1
    ent["name"] = "calculated data"
    ent["description"] = "Result data calculated by Newton's method"
    ent["keyword"] = "biological origin data"
    ent["accessRights"] = "Unrestricted Open Sharing"
    ent["availabilityStarts"] = "9999-04-01"
    ent["reasonForConcealment"] = "Because the dataset contains personal information."
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["contentSize"] = "100GB"
    ent["gotInformedConsent"] = "yes"
    ent["informedConsentFormat"] = "AMED"
    ent["identifier"] = [ClinicalResearchRegistration("https://jrct.niph.go.jp/latest-detail/jRCT202211111111")]

    jsonld = {'@type': 'DMP', '@id': '#dmp:1', 'name': 'calculated data', 'description': "Result data calculated by Newton's method", 'dataNumber': 1, 'keyword': 'biological origin data', 'accessRights': 'Unrestricted Open Sharing', 'availabilityStarts': '9999-04-01', 'reasonForConcealment': 'Because the dataset contains personal information.',
              'repository': {'@id': 'https://doi.org/xxxxxxxx'}, 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'contentSize': '100GB', 'gotInformedConsent': 'yes', 'informedConsentFormat': 'AMED', 'identifier': [{'@id': 'https://jrct.niph.go.jp/latest-detail/jRCT202211111111'}]}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = DMP("#dmp:1", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    # error: availabilityStarts value is not future date
    ent["description"] = "Result data calculated by Newton's method"
    ent["keyword"] = 1
    ent["accessRights"] = "Unrestricted Open Sharing"
    ent["availabilityStarts"] = "2022-04-01"
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["gotInformedConsent"] = "yes"
    ent["informedConsentFormat"] = "AMED"
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    del ent["unknown_property"]
    ent["name"] = "calculated data"
    ent["dataNumber"] = 1
    ent["keyword"] = "biological origin data"
    ent["availabilityStarts"] = "9999-04-01"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    ent = DMP("#dmp:1", {"accessRights": "Unshared", "gotInformedConsent": "yes"})
    crate.add(ent)

    # error: No DMPMetadata entity
    # error: availabilityStarts is required
    # error: informedConsentFormat is required
    # error: dataNumber is required
    with pytest.raises(EntityError):
        ent.validate(crate)

    meta = DMPMetadata()
    crate.add(meta)
    ent["availabilityStarts"] = "2000-01-01"
    ent["informedConsentFormat"] = "amed"
    ent["dataNumber"] = 1
    # error: repository is required
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["repository"] = "https://example.com/repo"
    # error: availabilityStarts MUST be the date of future
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["availabilityStarts"] = "2030-01-01"
    ent["repository"] = {"@id": "https://example.com/repo"}
    crate.add(RepositoryObject("https://example.com/repo"))
    # no error
    ent.validate(crate)

    ent["accessRights"] = "Unrestricted Open Sharing"
    # error: availabilityStarts is not required.
    # error: distribution is required.
    with pytest.raises(EntityError):
        ent.validate(crate)

    del ent["availabilityStarts"]
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["contentSize"] = "10GB"
    file = File("test", {"contentSize": "11GB", "dmpDataNumber": ent})
    crate.add(file, DataDownload("https://zenodo.org/record/example"))
    # error: file size is over.
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["contentSize"] = "100GB"
    # no error
    ent.validate(crate)
