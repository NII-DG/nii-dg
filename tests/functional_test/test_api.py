#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from time import sleep
from typing import Any

import pytest

from nii_dg.api import create_app

HERE = Path(__file__).parent.resolve()

PAYLOAD_SAMPLE_CRATE_PATH = HERE.joinpath("../example/sample_crate.json").resolve()
PAYLOAD_INVALID_CRATE_1_PATH = HERE.joinpath("../example/invalid_crate1.json").resolve()
PAYLOAD_INVALID_CRATE_2_PATH = HERE.joinpath("../example/invalid_crate2.json").resolve()


@pytest.fixture
def client():  # type: ignore
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_healthcheck(client: Any) -> None:
    res = client.get("/healthcheck")
    assert res.status_code == 200
    assert res.get_json() == {"message": "OK"}


def test_validation_post_request(client: Any) -> None:
    with PAYLOAD_SAMPLE_CRATE_PATH.open("r", encoding="utf-8") as f:
        payload = f.read()
    res = client.post("/validate", data=payload, content_type="application/json")
    assert res.status_code == 200
    json_data = res.get_json()
    assert "request_id" in json_data


def test_get_results(client: Any) -> None:
    # post request first
    with PAYLOAD_SAMPLE_CRATE_PATH.open("r", encoding="utf-8") as f:
        payload = f.read()
    res = client.post("/validate", data=payload, content_type="application/json")
    json_data = res.get_json()
    request_id = json_data["request_id"]

    # get results
    res = client.get(f"/{request_id}")
    assert res.status_code == 200
    json_data = res.get_json()

    assert "requestId" in json_data
    assert "request" in json_data
    assert "status" in json_data
    assert "results" in json_data
    assert json_data["requestId"] == request_id


def test_get_invalid_endpoint(client: Any) -> None:
    res = client.get("/invalid_endpoint")
    assert res.status_code == 400


def test_validation_complete(client: Any) -> None:
    # post request first
    with PAYLOAD_SAMPLE_CRATE_PATH.open("r", encoding="utf-8") as f:
        payload = f.read()
    res = client.post("/validate", data=payload, content_type="application/json")
    json_data = res.get_json()
    request_id = json_data["request_id"]

    # get results
    for _ in range(10):
        sleep(2)
        res = client.get(f"/{request_id}")
        json_data = res.get_json()
        if json_data["status"] == "COMPLETE":
            break

    assert json_data["status"] == "COMPLETE"
    assert len(json_data["results"]) == 0


def test_validation_complete_with_entity_ids(client: Any) -> None:
    # post request first
    with PAYLOAD_SAMPLE_CRATE_PATH.open("r", encoding="utf-8") as f:
        payload = f.read()
    res = client.post("/validate?entityIds=file_1.txt", data=payload, content_type="application/json")
    json_data = res.get_json()
    request_id = json_data["request_id"]

    # get results
    for _ in range(10):
        sleep(2)
        res = client.get(f"/{request_id}")
        json_data = res.get_json()
        if json_data["status"] == "COMPLETE":
            break

    assert json_data["status"] == "COMPLETE"
    assert len(json_data["results"]) == 0


def test_validation_failed_1(client: Any) -> None:
    # post request first
    with PAYLOAD_INVALID_CRATE_1_PATH.open("r", encoding="utf-8") as f:
        payload = f.read()
    res = client.post("/validate", data=payload, content_type="application/json")
    json_data = res.get_json()
    request_id = json_data["request_id"]

    # get results
    for _ in range(10):
        sleep(2)
        res = client.get(f"/{request_id}")
        json_data = res.get_json()
        if json_data["status"] == "FAILED":
            break

    assert json_data["status"] == "FAILED"
    assert len(json_data["results"]) == 2

    assert json_data["results"][0]["entityId"] == "https://example.com/person"
    assert json_data["results"][0]["props"] == "cao.Person:@id"
    assert "Failed to access the URL." in json_data["results"][0]["reason"]
    assert json_data["results"][1]["entityId"] == "#ginmonitoring"
    assert json_data["results"][1]["props"] == "ginfork.GinMonitoring:experimentPackageList"
    assert "Required Dataset entity is missing" in json_data["results"][1]["reason"]


def test_validation_failed_2(client: Any) -> None:
    """
    Failed with check_props error. Therefore, 400 error is returned at the POST request.
    """
    with PAYLOAD_INVALID_CRATE_2_PATH.open("r", encoding="utf-8") as f:
        payload = f.read()
    res = client.post("/validate", data=payload, content_type="application/json")
    assert res.status_code == 400
    json_data = res.get_json()
    assert "message" in json_data
    assert "400 Bad Request" in json_data["message"]
    assert "CrateCheckPropsError" in json_data["message"]
    assert "Errors occurred in <cao.File file_1.txt>" in json_data["message"]
