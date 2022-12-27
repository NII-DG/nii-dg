#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.ginfork import GinMonitoring


def test_init() -> None:
    ent = GinMonitoring("test")
    assert ent["@id"] == "test"
    assert ent["@type"] == "GinMonitoring"


def test_schema() -> None:
    ent = GinMonitoring("test")
    assert ent.schema == "ginfork"


def test_check_props() -> None:
    ent = GinMonitoring("test")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = GinMonitoring("test", {"name": "test"})

    jsonld = {
        "@id": "test",
        "@type": "GinMonitoring",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/ginfork/GinMonitoring.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
