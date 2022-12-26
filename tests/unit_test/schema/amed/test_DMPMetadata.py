#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.amed import DMPMetadata


def test_init() -> None:
    ent = DMPMetadata()
    assert ent["@id"] == "#AMED-DMP"
    assert ent["@type"] == "DMPMetadata"
    assert ent["name"] == "AMED-DMP"


def test_schema() -> None:
    ent = DMPMetadata()
    assert ent.schema == "amed"


def test_check_props() -> None:
    ent = DMPMetadata()

    # error
    with pytest.raises(PropsError):
        ent.check_props()


def test_as_jsonld() -> None:
    pass
