#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import (DataDownload, Organization, Person,
                                RepositoryObject, RootDataEntity)
from nii_dg.schema.meti import DMP, DMPMetadata


def test_init() -> None:
    ent = DMPMetadata({})
    assert ent["@id"] == "#METI-DMP"
    assert ent["@type"] == "DMPMetadata"
    assert ent.schema_name == "meti"
    assert ent.entity_name == "DMPMetadata"


def test_as_jsonld() -> None:
    ent = DMPMetadata({})

    ent["about"] = RootDataEntity({})
    ent["funder"] = Organization("https://ror.org/04ksd4g47")
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["hasPart"] = [DMP(1), DMP(2)]

    jsonld = {'@type': 'DMPMetadata', '@id': '#METI-DMP', 'about': {'@id': './'}, 'name': 'METI-DMP', 'funder': {'@id': 'https://ror.org/04ksd4g47'}, 'repository': {
        '@id': 'https://doi.org/xxxxxxxx'}, 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'hasPart': [{'@id': '#dmp:1'}, {'@id': '#dmp:2'}]}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = DMPMetadata({"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(PropsError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: type error
    ent["about"] = RootDataEntity({})
    ent["funder"] = "NII"
    ent["hasPart"] = [DMP(1), DMP(2)]
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["funder"] = Organization("https://ror.org/04ksd4g47")
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
