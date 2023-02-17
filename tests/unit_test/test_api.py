#!/usr/bin/env python3
# coding: utf-8

import json
import time
from concurrent.futures import Future
from typing import Any, Dict
from uuid import uuid4

import pytest
from flask import Flask

from nii_dg.api import create_app, job_map, request_map
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import ContactPoint, File, Organization


@pytest.fixture(scope="module")
def app() -> Flask:
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    return app


@pytest.fixture(scope="module")
def client(app: Flask) -> Any:
    yield app.test_client()
    app.test_client().delete()


@pytest.fixture(scope="module")
def crate_json() -> Dict[str, Any]:
    crate = ROCrate()
    crate.root["name"] = "test"
    file = File("path/to/file", {"name": "test_file", "contentSize": "10B"})
    crate.add(file)
    return crate.as_jsonld()


@pytest.fixture(scope="module")
def invalid_crate_json() -> Dict[str, Any]:
    crate = ROCrate()
    crate.root["name"] = "test"
    base_json = crate.as_jsonld()
    base_json["unknown"] = "invalid property"
    return base_json


@pytest.fixture(scope="module")
def crate_json_valiation_error() -> Dict[str, Any]:
    crate = ROCrate()
    crate.root["name"] = "test"
    # correct: National Institute of Informatics
    nii = Organization("https://ror.org/04ksd4g47", {"name": "NII"})
    crate.root["funder"] = [nii]
    cp = ContactPoint("#mailto:test@example.com", {"email": "sample@example.com"})
    crate.add(nii, cp)
    return crate.as_jsonld()


def test_validation(client: Any, crate_json: Dict[str, Any]) -> None:
    '''\
    - RO-Crate whole validation
    - successfully validated and no GovernanceError occurred
    '''
    req_response = client.post("/validate", json=json.dumps(crate_json))
    result = req_response.json

    assert "request_id" in result

    time.sleep(5)
    request_id = result["request_id"]
    result_response = client.get("/" + request_id).json

    assert result_response["request"]["entityIds"] == []
    assert result_response["request"]["roCrate"] == crate_json
    assert result_response["requestId"] == request_id
    assert result_response["status"] == "COMPLETE"
    assert result_response["results"] == []


def test_partial_valiadtion(client: Any, crate_json: Dict[str, Any]) -> None:
    '''\
    - validation only some entities in RO-Crate
    - successfully validated and no GovernanceError occurred
    '''
    req_response = client.post("/validate", json=json.dumps(crate_json), query_string={"entityId": ["./", "path/to/file"]})
    result = req_response.json

    assert "request_id" in result

    time.sleep(5)
    request_id = result["request_id"]
    result_response = client.get("/" + request_id).json

    assert result_response["request"]["entityIds"] == ["./", "path/to/file"]
    assert result_response["request"]["roCrate"] == crate_json
    assert result_response["requestId"] == request_id
    assert result_response["status"] == "COMPLETE"
    assert result_response["results"] == []


def test_vaidation_error(client: Any, crate_json_validation_error: Dict[str, Any]) -> None:
    '''\
    - RO-Crate whole validation
    - GovernanceError occurred
    '''
    req_response = client.post("/validate", json=json.dumps(crate_json_validation_error))
    result = req_response.json

    assert "request_id" in result

    time.sleep(5)
    request_id = result["request_id"]
    result_response = client.get("/" + request_id).json

    assert result_response["request"]["entityIds"] == []
    assert result_response["request"]["roCrate"] == crate_json
    assert result_response["requestId"] == request_id
    assert result_response["status"] == "FAILED"
    assert result_response["results"] == [
        {"entityId": "https://ror.org/04ksd4g47",
         "props": "base.Organization:name",
         "reason": "The value MUST be same as the registered name in ROR. See https://ror.org/04ksd4g47."},
        {"entityId": "#mailto:test@example.com",
         "props": "base.ContactPoint:@id",
         "reason": "The contained email is not the same as the value of email property."},
        {"entityId": "#mailto:test@example.com",
         "props": "base.ContactPoint:email",
         "reason": "The value is not the same as the email contained in the value of @id property."}]


def test_partial_vaidation_error(client: Any, crate_json_validation_error: Dict[str, Any]) -> None:
    '''\
    - validation only some entities in RO-Crate
    - GovernanceError occurred
    '''
    req_response = client.post("/validate", json=json.dumps(crate_json_validation_error), query_string={"entityId": ["#mailto:test@example.com"]})
    result = req_response.json

    assert "request_id" in result

    time.sleep(5)
    request_id = result["request_id"]
    result_response = client.get("/" + request_id).json

    assert result_response["request"]["entityIds"] == []
    assert result_response["request"]["roCrate"] == crate_json
    assert result_response["requestId"] == request_id
    assert result_response["status"] == "FAILED"
    assert result_response["results"] == [
        {"entityId": "#mailto:test@example.com",
         "props": "base.ContactPoint:@id",
         "reason": "The contained email is not the same as the value of email property."},
        {"entityId": "#mailto:test@example.com",
         "props": "base.ContactPoint:email",
         "reason": "The value is not the same as the email contained in the value of @id property."}]


def test_request_error_nocrate(client: Any) -> None:
    '''\
    - requests with no ro-crate
    - status code 400 is returned
    '''
    req_response = client.post("/validate")
    result = req_response.json

    assert req_response.status_code == 400
    assert result["message"] == "To data governance, ro-crate-metadata.json is required as a request body."


def test_request_invalid_crate(client: Any, invalid_crate_json: Dict[str, Any]) -> None:
    '''\
    - requests with invalid ro-crate (cannot make it into ROCrate instance)
    - status code 400 is returned
    '''

    req_response = client.post("/validate", json=json.dumps(invalid_crate_json))
    result = req_response.json

    assert req_response.status_code == 400
    assert result["message"] == "Invalid ro-crate."


def test_invalid_entityids(client: Any, crate_json: Dict[str, Any]) -> None:
    '''\
    - requests with invalid entityIds
    - status code 400 is returned
    '''
    req_response = client.post("/validate", json=json.dumps(crate_json), query_string={"entityId": ["unknownId"]})
    result = req_response.json

    assert req_response.status_code == 400
    assert result["message"] == "Invalid entityId: unknownId is not found in the crate."


def test_invalid_requestid(client: Any) -> None:
    '''\
    - requests with invalid requestId
    - status code 400 is returned
    '''
    invalid_uuid = str(uuid4())
    req_response = client.get("/" + invalid_uuid)
    result = req_response.json

    assert req_response.status_code == 400
    assert result["message"] == f"request_id {invalid_uuid} is not found."


def test_invalid_requestid_cancel(client: Any) -> None:
    '''\
    - requests with invalid requestId for cancel
    - status code 400 is returned
    '''
    invalid_uuid = str(uuid4())
    req_response = client.post("/validate" + invalid_uuid + "/cancel")
    result = req_response.json

    assert req_response.status_code == 400
    assert result["message"] == f"request_id {invalid_uuid} is not found."


def test_in_queue(client: Any) -> None:
    test_job: Future = Future()
    job_map[request_id] = test_job
