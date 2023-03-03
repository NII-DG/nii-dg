#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.error import EntityError
from nii_dg.schema.base import RepositoryObject


def test_init() -> None:
    ent = RepositoryObject("https://doi.org/xxxxxxxx")
    assert ent["@id"] == "https://doi.org/xxxxxxxx"
    assert ent["@type"] == "RepositoryObject"
    assert ent.schema_name == "base"
    assert ent.entity_name == "RepositoryObject"


def test_as_jsonld() -> None:
    ent = RepositoryObject("https://doi.org/xxxxxxxx")

    ent["name"] = "Gakunin RDM"
    ent["description"] = "Repository managed by NII."

    jsonld = {'@type': 'RepositoryObject', '@id': 'https://doi.org/xxxxxxxx', 'name': 'Gakunin RDM', 'description': 'Repository managed by NII.'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = RepositoryObject("https: // doi.org/xxxxxxxx", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    del ent["unknown_property"]
    ent["name"] = ["Gakunin RDM"]
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    ent["name"] = "Gakunin RDM"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
