#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import (ContactPoint, DataDownload, HostingInstitution,
                                License, Organization, RepositoryObject)
from nii_dg.schema.meti import DMP, DMPMetadata, File


def test_init() -> None:
    ent = DMP("#dmp:1")
    assert ent["@id"] == "#dmp:1"
    assert ent["@type"] == "DMP"
    assert ent.schema_name == "meti"
    assert ent.entity_name == "DMP"


def test_as_jsonld() -> None:
    ent = DMP("#dmp:1")

    ent["dataNumber"] = 1
    ent["name"] = "calculated data"
    ent["description"] = "Result data calculated by Newton's method"
    ent["hostingInstitution"] = HostingInstitution("https://ror.org/04ksd4g47")
    ent["wayOfManage"] = "commissioned"
    ent["accessRights"] = "open access"
    ent["reasonForConcealment"] = "To ensure market competitiveness for commercialization"
    ent["availabilityStarts"] = "9999-04-01"
    ent["creator"] = [Organization("https://ror.org/04ksd4g47")]
    ent["measurementTechnique"] = "Obtained using simulation software."
    ent["isAccessibleForFree"] = True
    ent["license"] = License("https://www.apache.org/licenses/LICENSE-2.0")
    ent["usageInfo"] = "Contact data manager before usage of this data set."
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["contentSize"] = "100GB"
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["contactPoint"] = ContactPoint("#mailto:contact@example.com")

    jsonld = {'@type': 'DMP', '@id': '#dmp:1', 'name': 'calculated data', 'description': "Result data calculated by Newton's method", 'dataNumber': 1, 'hostingInstitution': {'@id': 'https://ror.org/04ksd4g47'}, 'wayOfManage': 'commissioned', 'accessRights': 'open access', 'reasonForConcealment': 'To ensure market competitiveness for commercialization', 'availabilityStarts': '9999-04-01', 'creator': [
        {'@id': 'https://ror.org/04ksd4g47'}], 'measurementTechnique': 'Obtained using simulation software.', 'isAccessibleForFree': True, 'license': {'@id': 'https://www.apache.org/licenses/LICENSE-2.0'}, 'usageInfo': 'Contact data manager before usage of this data set.', 'repository': {'@id': 'https://doi.org/xxxxxxxx'}, 'contentSize': '100GB', 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'contactPoint': {'@id': '#mailto:contact@example.com'}}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = DMP("#dmp:1", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    # error: availabilityStarts value is not future date
    ent["dataNumber"] = 1
    ent["description"] = "Result data calculated by Newton's method"
    ent["hostingInstitution"] = HostingInstitution("https://ror.org/04ksd4g47")
    ent["wayOfManage"] = True
    ent["accessRights"] = "open access"
    ent["availabilityStarts"] = "2022-12-01"
    ent["creator"] = [Organization("https://ror.org/04ksd4g47")]
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    del ent["unknown_property"]
    ent["name"] = "calculated data"
    ent["availabilityStarts"] = "9999-12-01"
    ent["wayOfManage"] = "commissioned"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    ent = DMP("#dmp:1", {"accessRights": "embargoed access"})
    crate.add(ent)

    # error: availabilityStarts is required
    # error: reasonForConcealment is required
    # error: contactPoint is required
    # error: no DMPMetadata entity
    with pytest.raises(EntityError):
        ent.validate(crate)

    meta = DMPMetadata()
    crate.add(meta)
    ent["availabilityStarts"] = "2000-01-01"
    ent["reasonForConcealment"] = "Including personal info."
    ent["contactPoint"] = ContactPoint("#mailto:test@example.com")
    # error: availabilityStarts MUST be the date of future
    # error: repository is required
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["availabilityStarts"] = "2030-01-01"
    ent["repository"] = {"@id": "https://example.com/repo"}
    crate.add(RepositoryObject("https://example.com/repo"), ContactPoint("#mailto:test@example.com"))
    # no error
    ent.validate(crate)

    ent["accessRights"] = "open access"
    # error: availabilityStarts is not required
    # error: distribution is required
    # error: license is required
    # error: isAccessibleForFree is required
    with pytest.raises(EntityError):
        ent.validate(crate)

    del ent["availabilityStarts"]
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["license"] = License("https://example.com/license")
    ent["isAccessibleForFree"] = False
    ent["contentSize"] = "10GB"
    file = File("test", {"contentSize": "11GB", "dmpDataNumber": ent})
    crate.add(file, DataDownload("https://zenodo.org/record/example"), License("https://example.com/license"))
    # error: file size is over.
    # error: isAccessibleForFree MUST be True
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["contentSize"] = "100GB"
    ent["isAccessibleForFree"] = True
    # no error
    ent.validate(crate)
