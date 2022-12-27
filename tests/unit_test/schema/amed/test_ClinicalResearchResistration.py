#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.amed import ClinicalResearchResistration


def test_init() -> None:
    ent = ClinicalResearchResistration("https://example.com/ClinicalResearchResistration")
    assert ent["@id"] == "test"
    assert ent["@type"] == "ClinicalResearchResistration"


def test_schema() -> None:
    ent = ClinicalResearchResistration("https://example.com/ClinicalResearchResistration")
    assert ent.schema == "amed"


def test_check_props() -> None:
    ent = ClinicalResearchResistration("https://example.com/ClinicalResearchResistration")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = ClinicalResearchResistration("https://example.com/ClinicalResearchResistration", {"name": "test"})

    jsonld = {
        "@id": "https://example.com/ClinicalResearchResistration",
        "@type": "ClinicalResearchResistration",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/amed/ClinicalResearchResistration.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
