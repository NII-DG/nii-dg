#!/usr/bin/env python3
# coding: utf-8

import pytest
from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.ginfork import File


def test_init() -> None:
    ent = File("config/setting.txt")
    assert ent["@id"] == "config/setting.txt"
    assert ent["@type"] == "File"
    assert ent.schema_name == "ginfork"
    assert ent.entity_name == "File"


def test_as_jsonld() -> None:
    ent = File("config/setting.txt")

    ent["name"] = "setting.txt"
    ent["contentSize"] = "1560B"
    ent["encodingFormat"] = "text/plain"
    ent["sha256"] = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    ent["url"] = "https://github.com/username/repository/file"
    ent["sdDatePublished"] = "2022-12-01"
    ent["experimentPackageFlag"] = True

    jsonld = {'@type': 'File', '@id': 'config/setting.txt', 'name': 'setting.txt', 'contentSize': '1560B', 'encodingFormat': 'text/plain',
              'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'url': 'https://github.com/username/repository/file', 'sdDatePublished': '2022-12-01', 'experimentPackageFlag': True}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = File("file:///config/setting.txt", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: type error
    # error: @id value is not relative path nor URL
    # error: sdDatePublished value is not past date
    ent["sdDatePublished"] = "9999-12-01"
    ent["experimentPackageFlag"] = 1
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    del ent["unknown_property"]
    ent["@id"] = "config/setting/txt"
    ent["name"] = "setting.txt"
    ent["sdDatePublished"] = "2000-01-01"
    ent["experimentPackageFlag"] = True
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    file = File("https://example.com/config/setting.txt")

    # error: when @id is URL, sdDatePublished is required
    # error: contentSize is required
    with pytest.raises(EntityError):
        file.validate(crate)

    # no error occurs with sdDatePublished property
    file["contentSize"] = "150GB"
    file["sdDatePublished"] = "2000-01-01"
    file.validate(crate)

    # no error occurs with non-URL @id
    file["@id"] = "/config/setting.txt"
    del file["sdDatePublished"]
    file.validate(crate)
