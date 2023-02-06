#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import (DataDownload, Organization, RepositoryObject,
                                RootDataEntity)
from nii_dg.schema.cao import DMP, DMPMetadata


def test_init() -> None:
    ent = DMPMetadata(props={})
    assert ent["@id"] == "#CAO-DMP"
    assert ent["@type"] == "DMPMetadata"
    assert ent.schema_name == "cao"
    assert ent.entity_name == "DMPMetadata"


def test_as_jsonld() -> None:
    ent = DMPMetadata(props={})

    ent["about"] = RootDataEntity({})
    ent["funder"] = Organization("https://ror.org/04ksd4g47")
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["keyword"] = "Informatics"
    ent["eradProjectId"] = "123456"
    ent["hasPart"] = [DMP(1), DMP(2)]

    jsonld = {'@type': 'DMPMetadata', '@id': '#CAO-DMP', 'about': {'@id': './'}, 'name': 'CAO-DMP', 'funder': {'@id': 'https://ror.org/04ksd4g47'}, 'repository': {
        '@id': 'https://doi.org/xxxxxxxx'}, 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'keyword': 'Informatics', 'eradProjectId': '123456', 'hasPart': [{'@id': '#dmp:1'}, {'@id': '#dmp:2'}]}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = DMPMetadata(props={"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    ent["funder"] = Organization("https://ror.org/04ksd4g47")
    ent["keyword"] = 13
    ent["hasPart"] = [DMP(1), DMP(2)]
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    ent["about"] = RootDataEntity({})
    del ent["unknown_property"]
    ent["keyword"] = "Informatics"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    org = Organization("https://ror.org/04ksd4g47")
    root = RootDataEntity()
    ent = DMPMetadata(props={"funder": org, "hasPart": [], "about": root})
    crate.add(org, ent)

    # error: funder not included in the funder list of RootDataEntity
    # error: value of about is not the RootDataEntity of the crate
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["about"] = crate.root
    crate.root["funder"] = [org]
    # no error
    ent.validate(crate)

    dmp = DMP(1)
    crate.add(dmp)
    # error: not all DMP entity in the crate is included in hasPart
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["hasPart"] = [dmp]
    # no error
    ent.validate(crate)
