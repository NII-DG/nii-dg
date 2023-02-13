#!/usr/bin/env python3
# coding: utf-8

import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from flask import Blueprint, Flask, Response, abort, jsonify, request

from nii_dg.error import GovernanceError
from nii_dg.ro_crate import ROCrate

GET_STATUS_CODE = 200
POST_STATUS_CODE = 200
JOB_STATUS = [
    "UNKNOWN",
    "QUEUED",
    "RUNNING",
    "COMPLETE",
    "FAILED",
    "CANCELING",
    "CANCELED",
]


# --- state ---


executor = ThreadPoolExecutor(max_workers=3)
job_map: dict = {}
request_map: dict = {}


# --- controller ---

app_bp = Blueprint("app", __name__)


@app_bp.errorhandler(400)
def invalid_crate(e: Exception) -> Response:
    return jsonify(message=str(e)), 400


@app_bp.route('/validate', methods=['POST'])
def request_validation() -> Response:
    request_id = str(uuid4())
    request_body = request.json or {}
    entity_ids = request.args.get("entityIds", None)

    with current_app.app_context():  # noqa:F821
        request_map[request_id] = request_body

    if request_body == {}:
        # TODO
        raise Exception("To data governance, ro-crate-metadata.json is required as a request body.")

    # TODO: id記録してvalidate()実行
    job = executor.submit(validate, request_body, entity_ids)
    job_map[request_id] = job

    return jsonify({"request_id": request_id}), 200


@app_bp.route('/<request_id:str>', methods=['GET'])
def get_results() -> None:
    if request_id not in job_map:
        abort(400, "request_id not found")
    job = job_map[request_id]
    request = request_map[request_id]

    # TODO: add status and return result
    pass


@app_bp.route('/<request_id:str>/cancel', methods=['POST'])
def cancel_validation() -> None:
    if request_id not in job_map:
        abort(400, "request_id not found")
    job = job_map[request_id]
    try_cancel = job.cancel()
    if not try_cancel:
        abort(400, "Failed to cancel")
    response: Response = jsonify({"request_id": request_id})
    response.status_code = POST_STATUS_CODE

    # TODO

    return response


@app_bp.route('/healthcheck', methods=['GET'])
def check_health() -> Response:
    return Response(jsonify({"message": "OK"}), status=200)

# --- job ---


def validate(request: Dict[str, Any], entity_ids: Optional[List[str]]) -> List[Dict[str, Any]]:
    crate = ROCrate(request)
    if entity_ids:
        # TODO
        pass
    else:
        try:
            crate.validate()
            # TODO
            pass
        except GovernanceError as e:
            # TODO
            return str(e.entity_errors)


# --- app ---

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(app_bp)

    # for debug
    app.config["FLASK_ENV"] = "development"
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    return app


def main() -> None:
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
