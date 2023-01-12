#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import Dataset


def test_init() -> None:
    ent = Dataset("test")
    assert ent["@id"] == "test"
    assert ent["@type"] == "Dataset"


def test_schema() -> None:
    ent = Dataset("test")
    assert ent.schema_name == "base"


def test_check_props() -> None:
    ent = Dataset("test")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = Dataset("test", {"name": "test"})

    jsonld = {
        "@id": "test",
        "@type": "Dataset",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Dataset.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
