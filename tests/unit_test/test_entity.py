#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.entity import Entity, ROCrateMetadata
from nii_dg.schema.base import RootDataEntity


def test_delitem() -> None:
    ent = Entity("test", {"normal_prop": "removable", "@type": "unremovable"})

    del ent["normal_prop"]
    assert list(ent.keys()) == ["@id", "@type"]

    with pytest.raises(KeyError):
        del ent["@type"]


def test_as_jsonld() -> None:
    root = RootDataEntity({"name": "test"})
    meta = ROCrateMetadata(root)

    assert root.as_jsonld() == {
        "@id": "./",
        "@type": "Dataset",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/RootDataEntity.json"
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
    root = RootDataEntity()

    assert root.id == "./"
    assert root.type == "Dataset"
    assert root.context == "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/RootDataEntity.json"
    assert root.schema_name == "base"
    assert root.entity_name == "RootDataEntity"
