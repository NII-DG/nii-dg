#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.amed import DMP, DMPMetadata
from nii_dg.schema.base import HostingInstitution, Person, RootDataEntity


def test_init() -> None:
    ent = DMPMetadata()
    assert ent["@id"] == "#AMED-DMP"
    assert ent["@type"] == "DMPMetadata"
    assert ent["name"] == "AMED-DMP"


def test_schema() -> None:
    ent = DMPMetadata()
    assert ent.schema_name == "amed"


def test_check_props() -> None:
    ent = DMPMetadata()

    # error
    with pytest.raises(PropsError) as e1:
        ent.check_props()
    assert str(e1.value) == "The term about is required in <DMPMetadata #AMED-DMP>."

    with pytest.raises(PropsError) as e2:
        ent["about"] = "about"
        ent.check_props()
    assert str(e2.value) == "The term funding is required in <DMPMetadata #AMED-DMP>."

    with pytest.raises(PropsError) as e3:
        ent["funding"] = "sample project"
        ent.check_props()
    assert str(e3.value) == "The term chiefResearcher is required in <DMPMetadata #AMED-DMP>."

    with pytest.raises(PropsError) as e4:
        ent["chiefResearcher"] = "sample person"
        ent.check_props()
    assert str(e4.value) == "The term creator is required in <DMPMetadata #AMED-DMP>."

    with pytest.raises(PropsError) as e5:
        ent["creator"] = "sample person"
        ent.check_props()
    assert str(e5.value) == "The term hostingInstitution is required in <DMPMetadata #AMED-DMP>."

    with pytest.raises(PropsError) as e6:
        ent["hostingInstitution"] = "sample organization"
        ent.check_props()
    assert str(e6.value) == "The term dataManager is required in <DMPMetadata #AMED-DMP>."

    with pytest.raises(PropsError) as e7:
        ent["dataManager"] = "sample person"
        ent.check_props()
    assert str(e7.value) == "The term hasPart is required in <DMPMetadata #AMED-DMP>."

    with pytest.raises(PropsError) as e8:
        ent["hasPart"] = "sample dmp"
        ent.check_props()
    assert str(e8.value) == "The type of about in <DMPMetadata #AMED-DMP> MUST be nii_dg.schema.base.RootDataEntity; got str instead."

    with pytest.raises(PropsError) as e9:
        ent["about"] = RootDataEntity()
        ent.check_props()
    assert str(e9.value) == "The type of chiefResearcher in <DMPMetadata #AMED-DMP> MUST be nii_dg.schema.base.Person; got str instead."

    with pytest.raises(PropsError) as e10:
        test_person = Person("#test")
        ent["chiefResearcher"] = test_person
        ent.check_props()
    assert str(e10.value) == "The type of creator in <DMPMetadata #AMED-DMP> MUST be a list; got str instead."

    with pytest.raises(PropsError) as e11:
        ent["creator"] = ["test"]
        ent.check_props()
    assert str(e11.value) == "The type of creator[0] in <DMPMetadata #AMED-DMP> MUST be nii_dg.schema.base.Person; got str instead."

    with pytest.raises(PropsError) as e12:
        ent["creator"] = [test_person]
        ent.check_props()
    assert str(e12.value) == "The type of hostingInstitution in <DMPMetadata #AMED-DMP> MUST be nii_dg.schema.base.HostingInstitution; got str instead."

    with pytest.raises(PropsError) as e13:
        ent["hostingInstitution"] = HostingInstitution("#test")
        ent.check_props()
    assert str(e13.value) == "The type of dataManager in <DMPMetadata #AMED-DMP> MUST be nii_dg.schema.base.Person; got str instead."

    with pytest.raises(PropsError) as e14:
        ent["dataManager"] = test_person
        ent.check_props()
    assert str(e14.value) == "The type of hasPart in <DMPMetadata #AMED-DMP> MUST be a list; got str instead."

    with pytest.raises(PropsError) as e15:
        ent["hasPart"] = ["dmp"]
        ent.check_props()
    assert str(e15.value) == "The type of hasPart[0] in <DMPMetadata #AMED-DMP> MUST be nii_dg.schema.amed.DMP; got str instead."


def test_as_jsonld() -> None:
    ent = DMPMetadata(
        {
            "funding": "test funding"
        })
    ent["about"] = RootDataEntity()
    sample_person = Person("https://example.com/person")
    ent["chiefResearcher"] = sample_person
    ent["creator"] = [sample_person]
    ent["dataManager"] = sample_person

    ent["hostingInstitution"] = HostingInstitution("https://example.com")
    ent["hasPart"] = [DMP(1)]

    jsonld = {
        "@id": "#AMED-DMP",
        "@type": "DMPMetadata",
        "name": "AMED-DMP",
        "about": {"@id": "./"},
        "funding": "test funding",
        "chiefResearcher": {"@id": "https://example.com/person"},
        "creator": [{"@id": "https://example.com/person"}],
        "dataManager": {"@id": "https://example.com/person"},
        "hostingInstitution": {"@id": "https://example.com"},
        "hasPart": [{"@id": "#dmp:1"}],
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/amed/DMPMetadata.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
