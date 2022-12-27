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
    with pytest.raises(PropsError) as e1:
        root.check_props()
    assert str(e1.value) == "The term name is required in <Dataset ./>."

    with pytest.raises(PropsError) as e2:
        root["name"] = "test"
        root.check_props()
    assert str(e2.value) == "The term funder is required in <Dataset ./>."

    with pytest.raises(PropsError) as e3:
        root["funder"] = "test"
        root.check_props()
    assert str(e3.value) == "The type of funder in <Dataset ./> MUST be a list; got str instead."

    with pytest.raises(PropsError) as e4:
        root["funder"] = ["test"]
        root.check_props()
    assert str(e4.value) == "The type of funder[0] in <Dataset ./> MUST be nii_dg.schema.base.Organization; got str instead."

    with pytest.raises(PropsError) as e5:
        root["funder"] = [Organization("https://example.com")]
        root.check_props()
    assert str(e5.value) == "The type of funder[0] in <Dataset ./> MUST be nii_dg.schema.base.Organization; got str instead."


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


def test_validate() -> None:
    pass
