#!/usr/bin/env python3
# coding: utf-8

import os
from typing import Any, Dict

import pytest

from nii_dg.error import (CrateError, GovernanceError,
                          UnexpectedImplementationError)
from nii_dg.ro_crate import (ContextualEntity, DataEntity, DefaultEntity,
                             ROCrate, ROCrateMetadata, RootDataEntity)
from nii_dg.schema.base import File


def test_add() -> None:
    crate = ROCrate()

    meta = crate.get_by_entity_type(ROCrateMetadata)
    assert crate.default_entities == [crate.root, meta[0]]

    data_ent = DataEntity("data")
    con_ent = ContextualEntity("context")
    crate.add(data_ent, con_ent)

    assert crate.data_entities == [data_ent]
    assert crate.contextual_entities == [con_ent]

    # error
    def_ent = DefaultEntity("def")
    with pytest.raises(UnexpectedImplementationError):
        crate.add(def_ent)


def test_delete() -> None:
    crate = ROCrate()

    data_ent = DataEntity("data")
    con_ent = ContextualEntity("context")
    crate.add(data_ent, con_ent)

    crate.delete(data_ent)
    crate.delete(con_ent)

    assert crate.data_entities == []
    assert crate.contextual_entities == []

    # error
    with pytest.raises(UnexpectedImplementationError):
        crate.delete(crate.root)


def test_get_by_id() -> None:
    crate = ROCrate()

    assert crate.get_by_id("./") == [crate.root]
    assert crate.get_by_id("test") == []


def test_get_by_entity_type() -> None:
    crate = ROCrate()

    assert crate.get_by_entity_type(RootDataEntity) == [crate.root]


def test_get_by_id_and_entity_type() -> None:
    crate = ROCrate()
    # TODO
    pass


def test_get_all_entities() -> None:
    crate = ROCrate()
    meta = crate.get_by_id("ro-crate-metadata.json")

    assert crate.get_all_entities() == [crate.root, meta[0]]

    data_ent = DataEntity("data")
    con_ent = ContextualEntity("context")
    crate.add(data_ent, con_ent)

    assert crate.get_all_entities() == [crate.root, meta[0], data_ent, con_ent]


def test_as_json_ld() -> None:
    crate = ROCrate()
    crate.root["name"] = "test"

    test_dict = crate.as_jsonld()

    assert test_dict == {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [{
            "@id": "./",
            "@type": "Dataset",
            "name": "test",
            "hasPart": [],
            "datePublished":test_dict["@graph"][0]["datePublished"]
        },
            {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": {
                "@id": "https://w3id.org/ro/crate/1.1"
            },
            "about": {
                "@id": "./"
            }
        }]
    }


def test_check_duplicate_entity() -> None:
    crate = ROCrate()

    # error
    file_1 = File("test")
    file_2 = File("test")
    crate.add(file_1, file_2)

    with pytest.raises(CrateError):
        crate.check_duplicate_entity()

    # no error
    crate.delete(file_2)
    crate.check_duplicate_entity()


@pytest.fixture
def tmp_file() -> Any:
    with open("tmp.json", "x"):
        pass
    yield "tmp.json"
    os.remove("tmp.json")


def test_dump(tmp_file: str) -> None:
    crate = ROCrate()
    crate.root["name"] = "test"

    # no error
    crate.dump(tmp_file)


def test_validate() -> None:
    crate = ROCrate()
    crate.root["name"] = "test"

    # no error
    crate.validate()

    # error with File entity
    file = File("https://example.com/file")
    crate.add(file)

    with pytest.raises(GovernanceError):
        crate.validate()


def test_from_jsonld() -> None:
    test_jsonld: Dict[str, Any] = {"context": "test"}
    # error with no @context property
    with pytest.raises(CrateError):
        ROCrate(jsonld=test_jsonld)

    # error with value of @context property
    test_jsonld = {"@context": "test"}
    with pytest.raises(CrateError):
        ROCrate(jsonld=test_jsonld)

    # error with no @graph property
    test_jsonld["@context"] = ROCrate.BASE_CONTEXT
    with pytest.raises(CrateError):
        ROCrate(jsonld=test_jsonld)

    # error with no RootDataEntity
    test_jsonld["@graph"] = []
    with pytest.raises(CrateError):
        ROCrate(jsonld=test_jsonld)

    # error with no ROCrateMetadata
    test_jsonld["@graph"].append({"@id": "./", "@type": "Dataset"})
    with pytest.raises(CrateError):
        ROCrate(jsonld=test_jsonld)

    # successfully generating ro-crate instance
    test_jsonld["@graph"].append({"@id": "ro-crate-metadata.json", "@type": "CreativeWork"})

    crate_1 = ROCrate(jsonld=test_jsonld)
    isinstance(crate_1, ROCrate)
    assert len(crate_1.get_all_entities()) == 2
    assert len(crate_1.get_by_entity_type(RootDataEntity)) == 1
    assert len(crate_1.get_by_entity_type(ROCrateMetadata)) == 1

    # error with entity having no @id property
    test_jsonld = crate_1.as_jsonld()
    test_jsonld["@graph"].append({"id": "path/to/file"})
    print(test_jsonld)
    with pytest.raises(CrateError):
        ROCrate(jsonld=test_jsonld)

    # error with entity having no @type property
    del test_jsonld["@graph"][2]
    test_jsonld["@graph"].append({"@id": "path/to/file"})
    with pytest.raises(CrateError):
        ROCrate(jsonld=test_jsonld)

    # error with entity having no @context property
    test_jsonld["@graph"][2]["@type"] = "File"
    with pytest.raises(CrateError):
        ROCrate(jsonld=test_jsonld)

    # successfully generating ro-crate instance
    test_jsonld["@graph"][2]["@context"] = "https://raw.githubusercontent.com/NII-DG/nii_dg/main/schema/context/base.jsonld"
    crate_2 = ROCrate(jsonld=test_jsonld)
    isinstance(crate_2, ROCrate)
    assert len(crate_2.get_all_entities()) == 3
    assert len(crate_2.get_by_entity_type(File)) == 1
