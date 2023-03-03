#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.entity import Entity, ROCrateMetadata, RootDataEntity
from nii_dg.schema.base import Person


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


def test_properties() -> None:
    person = Person("https://example.com/person", {"name": "Ichiro Suzuki"})

    assert person.id == "https://example.com/person"
    assert person.type == "Person"
    assert person.schema_name == "base"
    assert person.entity_name == "Person"

    root = RootDataEntity()
    assert root.id == "./"
    assert root.type == "Dataset"
