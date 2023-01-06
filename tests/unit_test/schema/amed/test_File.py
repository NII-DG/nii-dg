#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.amed import DMP, File
from nii_dg.schema.base import DataDownload, RepositoryObject


def test_init() -> None:
    ent = File("/test")
    assert ent["@id"] == "/test"
    assert ent["@type"] == "File"


def test_schema() -> None:
    ent = File("/test")
    assert ent.schema == "amed"


def test_check_props() -> None:
    ent = File("file://test")

    # error
    with pytest.raises(PropsError) as e1:
        ent.check_props()
    assert str(e1.value) == "The term name is required in <File file://test>."

    with pytest.raises(PropsError) as e2:
        ent["name"] = "test"
        ent.check_props()
    assert str(e2.value) == "The term dmpDataNumber is required in <File file://test>."

    with pytest.raises(PropsError) as e3:
        ent["dmpDataNumber"] = "#1"
        ent.check_props()
    assert str(e3.value) == "The term contentSize is required in <File file://test>."

    with pytest.raises(PropsError) as e4:
        ent["contentSize"] = "156GB"
        ent.check_props()
    assert str(e4.value) == "The type of dmpDataNumber in <File file://test> MUST be nii_dg.schema.amed.DMP; got str instead."

    with pytest.raises(PropsError) as e5:
        ent["dmpDataNumber"] = DMP(1)
        ent.check_props()
    assert str(e5.value) == "The @id value in <File file://test> MUST be URL or relative path to the file, not absolute path."


def test_as_jsonld() -> None:
    ent = File("test", {
        "name": "testfile",
        "contentSize": "156GB",
        "encodingFormat": "text/plain"
    })
    ent["dmpDataNumber"] = DMP(1)

    jsonld = {
        "@id": "test",
        "@type": "File",
        "name": "testfile",
        "dmpDataNumber": {"@id": "#dmp:1"},
        "contentSize": "156GB",
        "encodingFormat": "text/plain",
        "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/amed/File.json"
    }

    assert ent.as_jsonld() == jsonld


def test_validate() -> None:
  pass
