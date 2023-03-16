#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.entity import ROCrateMetadata, RootDataEntity
from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Organization, Person


def test_delitem() -> None:
    with pytest.raises(KeyError):
        ent = Person("test", {"normal_prop": "removable", "@type": "not_settable"})

    ent = Person("test", {"normal_prop": "removable"})
    del ent["normal_prop"]
    assert "normal_prop" not in ent.keys()

    with pytest.raises(KeyError):
        del ent["@type"]


def test_as_jsonld() -> None:
    person = RootDataEntity({"name": "test"})
    meta = ROCrateMetadata(person)

    assert person.as_jsonld() == {
        "@id": "./",
        "@type": "Dataset",
        "name": "test"
    }
    assert meta.as_jsonld() == {
        "@id": "ro-crate-metadata.json",
        "@type": "CreativeWork",
        "conformsTo": {
            "@id": "https://w3id.org/ro/crate/1.1"
        },
        "about": {
            "@id": "./"
        }
    }


def test_validate() -> None:
    crate = ROCrate()
    ent = Person("https://example.com", {"name": "Ichiro Suzuki", "affiliation": "Mariners"})

    crate.add(ent)
    # error: the value of affiliation is wrong type
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["affiliation"] = {"name": "Mariners"}
    # error: the value of affiliation is wrong dict
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["affiliation"] = {"@id": "https://example.com/org"}
    # error: the entity linked by affiliation is not in crate
    with pytest.raises(EntityError):
        ent.validate(crate)

    org = Organization("https://example.com/org")
    crate.add(org)
    # no error
    ent.validate(crate)


def test_properties() -> None:
    person = Person("https://example.com/person", {"name": "Ichiro Suzuki"})

    assert person.id == "https://example.com/person"
    assert person.type == "Person"
    assert person.schema_name == "base"
    assert person.entity_name == "Person"

    root = RootDataEntity()
    assert root.id == "./"
    assert root.type == "Dataset"
