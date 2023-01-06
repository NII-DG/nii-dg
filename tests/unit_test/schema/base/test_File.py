#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import File


def test_init() -> None:
    ent = File("test")
    assert ent["@id"] == "test"
    assert ent["@type"] == "File"


def test_schema() -> None:
    ent = File("test")
    assert ent.schema == "base"


def test_check_props() -> None:
    ent = File("test")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = File("test", {"name": "test", "contentSize": "100GB"})

    jsonld = {
        "@id": "test",
        "@type": "File",
        "name": "test",
        "contentSize": "100GB",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/File.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
