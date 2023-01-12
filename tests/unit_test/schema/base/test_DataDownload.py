#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import DataDownload


def test_init() -> None:
    ent = DataDownload("https://example.com/DataDownload")
    assert ent["@id"] == "test"
    assert ent["@type"] == "DataDownload"


def test_schema() -> None:
    ent = DataDownload("https://example.com/DataDownload")
    assert ent.schema_name == "base"


def test_check_props() -> None:
    ent = DataDownload("https://example.com/DataDownload")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = DataDownload("https://example.com/DataDownload", {"name": "test"})

    jsonld = {
        "@id": "https://example.com/DataDownload",
        "@type": "DataDownload",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/DataDownload.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
