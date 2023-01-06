#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

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

    jsonld = {'@type': 'File', '@id': 'config/setting.txt', 'name': 'setting.txt', 'contentSize': '1560B', 'encodingFormat': 'text/plain', 'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'url': 'https://github.com/username/repository/file', 'sdDatePublished': '2022-12-01', 'experimentPackageFlag': True}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    # TO BE UPDATED
    pass


def test_validate() -> None:
    # TO BE UPDATED
    pass
