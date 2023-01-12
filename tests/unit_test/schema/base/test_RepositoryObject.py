#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import RepositoryObject


def test_init() -> None:
    ent = RepositoryObject("https://example.com/RepositoryObject")
    assert ent["@id"] == "test"
    assert ent["@type"] == "RepositoryObject"


def test_schema() -> None:
    ent = RepositoryObject("https://example.com/RepositoryObject")
    assert ent.schema_name == "base"


def test_check_props() -> None:
    ent = RepositoryObject("https://example.com/RepositoryObject")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = RepositoryObject("https://example.com/RepositoryObject", {"name": "test"})

    jsonld = {
        "@id": "https://example.com/RepositoryObject",
        "@type": "RepositoryObject",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/RepositoryObject.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
