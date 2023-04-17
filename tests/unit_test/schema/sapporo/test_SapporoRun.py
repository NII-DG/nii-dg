#!/usr/bin/env python3
# coding: utf-8

from typing import Any, Dict
from unittest.mock import mock_open, patch

import pytest

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.sapporo import Dataset, File, SapporoRun

# --- mock ---


def mocked_ignore_func(*args: Any, **kwargs: Any) -> None:
    # do nothing
    pass


def mocked_requests_get(*args: Any, **kwargs: Any) -> Any:
    # mock of get to sapporo_server
    class MockResponse:
        def __init__(self, json_data: Dict[str, Any], status_code: int) -> None:
            self.json_data = json_data
            self.status_code = status_code

        def json(self) -> Dict[str, Any]:
            return self.json_data

        def text(self) -> str:
            return str(self.json_data)

    return MockResponse({"state": "COMPLETE", "outputs":
                         [{'file_name': 'test_file', 'file_url': 'dummy_url'}]},
                        200)


def mocked_requests_post(*args: Any, **kwargs: Any) -> Any:
    # mock of post to sapporo_server
    class MockResponse:
        def __init__(self, json_data: Dict[str, Any], status_code: int) -> None:
            self.json_data = json_data
            self.status_code = status_code

        def json(self) -> Dict[str, Any]:
            return self.json_data

        def raise_for_status(self) -> None:
            pass

    return MockResponse({"run_id": "test"}, 200)


# --- tests ---
def test_init() -> None:
    ent = SapporoRun()
    assert ent["@id"] == "#sapporo-run"
    assert ent["@type"] == "SapporoRun"
    assert ent.schema_name == "sapporo"
    assert ent.entity_name == "SapporoRun"


def test_as_jsonld() -> None:
    ent = SapporoRun()

    ent["workflow_engine_name"] = "CWL"
    ent["sapporo_location"] = "https://example.com/sapporo"
    ent["state"] = "COMPLETE"
    ent["outputs"] = Dataset("outputs/", {"name": "outputs"})

    jsonld = {"@type": "SapporoRun", "@id": "#sapporo-run", "workflow_engine_name": "CWL",
              "sapporo_location": "https://example.com/sapporo", "state": "COMPLETE", "outputs": {"@id": "outputs/"}}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = SapporoRun(props={"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required property
    # error: type error
    ent["state"] = 100
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    del ent["unknown_property"]
    ent["workflow_engine_name"] = "CWL"
    ent["sapporo_location"] = "https://example.com/sapporo"
    ent["state"] = "COMPLETE"
    ent["outputs"] = Dataset("outputs/", {"name": "outputs"})
    ent.check_props()


@patch("pathlib.Path.mkdir", side_effect=mocked_ignore_func)
@patch("requests.get", side_effect=mocked_requests_get)
@patch("requests.post", side_effect=mocked_requests_post)
@patch("builtins.open", new_callable=mock_open)
@patch("os.path.getsize", return_value=10)
@patch("nii_dg.schema.sapporo.get_file_sha256", return_value="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")
@patch("shutil.rmtree", side_effect=mocked_ignore_func)
def test_validate(rmtree_mock: Any, sha256_mock: Any, getsize_mock: Any, open_mock: Any, post_mock: Any, get_mock: Any, mkdir_mock: Any) -> None:
    # TODO
    crate = ROCrate()
    output = Dataset("outputs/", {"name": "outputs", "hasPart": []})

    ent = SapporoRun(props={
        "state": "COMPLETE", "sapporo_location": "https://example.com/sapporo", "workflow_engine_name": "CWL"})
    ent["outputs"] = output

    crate.add(ent, output)

    # output file MUST be included in crate
    with pytest.raises(EntityError):
        ent.validate(crate)

    assert sha256_mock.call_count == 0
    assert getsize_mock.call_count == 0
    assert open_mock.call_count == 1
    assert post_mock.call_count == 1
    assert get_mock.call_count == 3
    assert mkdir_mock.call_count == 1

    # no error
    file = File("outputs/test_file", {"name": "test_file", "contentSize": "10B", "sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"})
    output["hasPart"].append(file)
    crate.add(file)
    ent.validate(crate)

    assert sha256_mock.call_count == 1
    assert getsize_mock.call_count == 1
    assert open_mock.call_count == 2
    assert post_mock.call_count == 2
    assert get_mock.call_count == 6
    assert mkdir_mock.call_count == 2
