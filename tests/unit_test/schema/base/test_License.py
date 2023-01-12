#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import License


def test_init() -> None:
    ent = License("https://example.com/License")
    assert ent["@id"] == "test"
    assert ent["@type"] == "License"


def test_schema() -> None:
    ent = License("https://example.com/License")
    assert ent.schema_name == "base"


def test_check_props() -> None:
    ent = License("https://example.com/License")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = License("https://example.com/License", {"name": "test"})

    jsonld = {
        "@id": "https://example.com/License",
        "@type": "License",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/License.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
