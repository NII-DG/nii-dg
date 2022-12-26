#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import Organization, RootDataEntity


def test_init() -> None:
    root = RootDataEntity()
    assert root["@id"] == "./"
    assert root["@type"] == "Dataset"


def test_schema() -> None:
    root = RootDataEntity()
    assert root.schema == "base"


def test_check_props() -> None:
    root = RootDataEntity()

    # error
    with pytest.raises(PropsError):
        root.check_props()


def test_as_jsonld() -> None:
    root = RootDataEntity({"name": "test"})
    root["funder"] = [Organization("https://example.com", {"name": "test_org"})]

    jsonld = {
        "@id": "./",
        "@type": "Dataset",
        "name": "test",
        "funder": [{"@id": "https://example.com"}],
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/RootDataEntity.json"
    }

    assert root.as_jsonld() == jsonld
