#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import (DataDownload, Organization, RepositoryObject,
                                RootDataEntity)
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
    ent = DMPMetadata(props={"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    ent["funder"] = "NII"
    ent["hasPart"] = [DMP(1), DMP(2)]
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    del ent["unknown_property"]
    ent["about"] = RootDataEntity({})
    ent["funder"] = Organization("https://ror.org/04ksd4g47")
    ent.check_props()


def test_validate() -> None:
    rocrate = ROCrate()
    org = Organization("https://ror.org/04ksd4g47")
    root = RootDataEntity()
    meta = DMPMetadata(props={"funder": org, "hasPart": [], "about": root})
    rocrate.add(org, meta)

    # error: funder not included in the funder list of RootDataEntity
    # error: value of about is not the RootDataEntity of the crate
    with pytest.raises(EntityError):
        meta.validate(rocrate)

    meta["about"] = rocrate.root
    rocrate.root["funder"] = [org]
    # no error
    meta.validate(rocrate)

    dmp = DMP(2)
    rocrate.add(dmp)
    # error: not all DMP entity in the crate is included in hasPart
    with pytest.raises(EntityError):
        meta.validate(rocrate)

    meta["hasPart"] = [dmp]
    # no error
    meta.validate(rocrate)
