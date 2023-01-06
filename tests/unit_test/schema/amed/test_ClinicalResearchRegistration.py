#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.schema.amed import ClinicalResearchRegistration


def test_init() -> None:
    ent = ClinicalResearchRegistration("https://example.com/ClinicalResearchRegistration")
    assert ent["@id"] == "test"
    assert ent["@type"] == "ClinicalResearchRegistration"


def test_schema() -> None:
    ent = ClinicalResearchRegistration("https://example.com/ClinicalResearchRegistration")
    assert ent.schema_name == "amed"


def test_check_props() -> None:
    ent = ClinicalResearchRegistration("https://example.com/ClinicalResearchRegistration")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_as_jsonld() -> None:
    ent = ClinicalResearchRegistration("https://example.com/ClinicalResearchRegistration", {"name": "test"})

    jsonld = {
        "@id": "https://example.com/ClinicalResearchRegistration",
        "@type": "ClinicalResearchRegistration",
        "name": "test",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/amed/ClinicalResearchRegistration.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
    pass
