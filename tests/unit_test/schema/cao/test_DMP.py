#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import (DataDownload, HostingInstitution, License,
                                RepositoryObject)
from nii_dg.schema.cao import DMP, Person


def test_init() -> None:
    ent = DMP(1)
    assert ent["@id"] == "#dmp:1"
    assert ent["@type"] == "DMP"
    assert ent.schema_name == "cao"
    assert ent.entity_name == "DMP"


def test_as_jsonld() -> None:
    ent = DMP(1)
    person = Person("https://orcid.org/0000-0001-2345-6789")

    ent["name"] = "calculated data"
    ent["description"] = "Result data calculated by Newton's method"
    ent["creator"] = [person]
    ent["keyword"] = "Informatics"
    ent["accessRights"] = "open access"
    ent["availabilityStarts"] = "2023-04-01"
    ent["isAccessibleForFree"] = True
    ent["license"] = License("https://www.apache.org/licenses/LICENSE-2.0")
    ent["usageInfo"] = "Contact data manager before usage of this data set."
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["contentSize"] = "100GB"
    ent["hostingInstitution"] = HostingInstitution("https://ror.org/04ksd4g47")
    ent["dataManager"] = person

    jsonld = {'@type': 'DMP', '@id': '#dmp:1', 'name': 'calculated data', 'description': "Result data calculated by Newton's method", 'dataNumber': 1, 'keyword': 'Informatics', 'accessRights': 'open access', 'availabilityStarts': '2023-04-01', 'isAccessibleForFree': True, 'license': {'@id': 'https://www.apache.org/licenses/LICENSE-2.0'},
              'usageInfo': 'Contact data manager before usage of this data set.', 'repository': {'@id': 'https://doi.org/xxxxxxxx'}, 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'contentSize': '100GB', 'hostingInstitution': {'@id': 'https://ror.org/04ksd4g47'}, 'dataManager': {'@id': 'https://orcid.org/0000-0001-2345-6789'}, 'creator': [{'@id': 'https://orcid.org/0000-0001-2345-6789'}]}

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
    person = Person("https://orcid.org/0000-0001-2345-6789")

    ent["name"] = "calculated data"
    ent["description"] = "Result data calculated by Newton's method"
    ent["creator"] = [person]
    ent["keyword"] = "Informatics"
    ent["accessRights"] = "open access"
    ent["availabilityStarts"] = 9999
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["hostingInstitution"] = HostingInstitution("https://ror.org/04ksd4g47")
    ent["dataManager"] = person
    with pytest.raises(PropsError):
        ent.check_props()

    # error: availabilityStarts value is not future date
    ent["availabilityStarts"] = "2022-12-01"
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["availabilityStarts"] = "9999-04-01"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
