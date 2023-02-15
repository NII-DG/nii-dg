#!/usr/bin/env python3
# coding: utf-8

from typing import Any, Dict

import pytest
from flask import Flask

from nii_dg.api import create_app
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Organization


@pytest.fixture()
def app() -> Flask:
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # 前処理・後処理が必要なら yield app
    return app


@pytest.fixture()
def client(app: Flask) -> Any:
    return app.test_client()


@pytest.fixture()
def crate_json() -> Dict[str, Any]:
    crate = ROCrate()
    crate.root["name"] = "test"
    return crate.as_jsonld()


@pytest.fixture()
def crate_json_error() -> Dict[str, Any]:
    crate = ROCrate()
    crate.root["name"] = "test"
    # correct: National Institute of Informatics
    nii = Organization("https://ror.org/04ksd4g47", {"name": "NII"})
    crate.root["funder"] = nii
    crate.add(nii)
    return crate.as_jsonld()


def test_request(client: Any, crate_json: Dict[str, Any]) -> None:
    # result = client.post("/", data=crate_json)
    # response = result.get_json()

    # assert 'request_id' in response
    pass


def test_request_error(client: Any, crate_json_error: Dict[str, Any]) -> None:
    # result = client.post("/", data=crate_json_error)
    # response = result.get_json()

    # assert 'request_id' in response
    pass
