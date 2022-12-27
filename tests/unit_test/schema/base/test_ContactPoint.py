#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import ContactPoint


def test_init() -> None:
    ent = ContactPoint("https://example.com/ContactPoint")
    assert ent["@id"] == "test"
    assert ent["@type"] == "ContactPoint"


def test_schema() -> None:
    ent = ContactPoint("https://example.com/ContactPoint")
    assert ent.schema == "base"


def test_check_props() -> None:
    ent = ContactPoint("https://example.com/ContactPoint")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = ContactPoint("https://example.com/ContactPoint", {"name": "test"})

    jsonld = {
        "@id": "https://example.com/ContactPoint",
        "@type": "ContactPoint",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/ContactPoint.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
