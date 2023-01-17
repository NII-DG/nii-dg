#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import DataDownload


def test_init() -> None:
    ent = DataDownload("https://zenodo.org/record/example")
    assert ent["@id"] == "https://zenodo.org/record/example"
    assert ent["@type"] == "DataDownload"
    assert ent.schema_name == "base"
    assert ent.entity_name == "DataDownload"


def test_as_jsonld() -> None:
    ent = DataDownload("https://zenodo.org/record/example")

    ent["description"] = "All data set is available from this URL as a zip file."
    ent["sha256"] = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    ent["uploadDate"] = "2022-12-01"

    jsonld = {'@type': 'DataDownload', '@id': 'https://zenodo.org/record/example', 'description': 'All data set is available from this URL as a zip file.',
              'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'uploadDate': '2022-12-01'}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = DataDownload("file:///config/setting.txt", {"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(PropsError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(PropsError):
        ent.check_props()

    # error: type error
    ent["uploadDate"] = 9999
    with pytest.raises(PropsError):
        ent.check_props()

    # error: @id value is not URL
    ent["uploadDate"] = "9999-01-01"
    with pytest.raises(PropsError):
        ent.check_props()

    # error: uploadDate value is not past date
    ent["@id"] = "https://example.com/download"
    with pytest.raises(PropsError):
        ent.check_props()

    # no error occurs with correct property value
    ent["uploadDate"] = "2022-12-01"
    ent.check_props()


def test_validate() -> None:
    # TO BE UPDATED
    pass
