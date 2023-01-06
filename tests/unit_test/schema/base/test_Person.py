#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import Person


def test_init() -> None:
    ent = Person("https://example.com/Person")
    assert ent["@id"] == "test"
    assert ent["@type"] == "Person"


def test_schema() -> None:
    ent = Person("https://example.com/Person")
    assert ent.schema == "base"


def test_check_props() -> None:
    ent = Person("https://example.com/Person")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = Person("https://example.com/Person", {"name": "test"})

    jsonld = {
        "@id": "https://example.com/Person",
        "@type": "Person",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Person.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
