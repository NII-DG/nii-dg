#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import (ContactPoint, DataDownload, HostingInstitution,
                                License, Organization, RepositoryObject)
from nii_dg.schema.meti import DMP


def test_init() -> None:
    ent = DMP(1)
    assert ent["@id"] == "#dmp:1"
    assert ent["@type"] == "DMP"
    assert ent.schema_name == "meti"
    assert ent.entity_name == "DMP"


def test_as_jsonld() -> None:
    ent = DMP(1)

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

    jsonld = {'@type': 'DMP', '@id': '#dmp:1', 'name': 'calculated data', 'description': "Result data calculated by Newton's method", 'hostingInstitution': {'@id': 'https://ror.org/04ksd4g47'}, 'wayOfManage': 'commissioned', 'accessRights': 'open access', 'reasonForConcealment': 'To ensure market competitiveness for commercialization', 'availabilityStarts': '9999-04-01', 'creator': [
        {'@id': 'https://ror.org/04ksd4g47'}], 'measurementTechnique': 'Obtained using simulation software.', 'isAccessibleForFree': True, 'license': {'@id': 'https://www.apache.org/licenses/LICENSE-2.0'}, 'usageInfo': 'Contact data manager before usage of this data set.', 'repository': {'@id': 'https://doi.org/xxxxxxxx'}, 'contentSize': '100GB', 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'contactPoint': {'@id': '#mailto:contact@example.com'}}

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
    ent["hostingInstitution"] = HostingInstitution("https://ror.org/04ksd4g47")
    ent["wayOfManage"] = "commissioned"
    ent["accessRights"] = "open access"
    ent["availabilityStarts"] = 9999
    ent["creator"] = [Organization("https://ror.org/04ksd4g47")]
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    with pytest.raises(PropsError):
        ent.check_props()

    # error: availabilityStarts value is not future date
    ent["availabilityStarts"] = "2022-12-01"
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["availabilityStarts"] = "9999-12-01"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
