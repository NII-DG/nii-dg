#!/usr/bin/env python3
# coding: utf-8

import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Dict, List, Optional
from uuid import uuid4

from flask import (Blueprint, Flask, Response, abort, current_app, jsonify,
                   request)

from nii_dg.error import CrateError, GovernanceError
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
job_map: Dict[str, Future] = {}
request_map: Dict[str, Dict[str, Any]] = {}


# --- controller ---

app_bp = Blueprint("app", __name__)


@app_bp.errorhandler(400)
def invalid_request(e: Exception) -> Response:
    return jsonify(message=str(e)), 400


@app_bp.route("/validate", methods=["POST"])
def request_validation() -> Response:
    request_id = str(uuid4())
    request_body = request.json or {}
    entity_ids = request.args.get("entityIds", None)

    with current_app.app_context():
        request_map[request_id] = request_body

    if request_body == {}:
        # TODO
        return abort(400, "To data governance, ro-crate-metadata.json is required as a request body.")

    job = executor.submit(validate, request_body, entity_ids)
    job_map[request_id] = job

    response: Response = jsonify({"request_id": request_id})
    response.status_code = POST_STATUS_CODE
    return response


@app_bp.route("/<string:request_id>", methods=["GET"])
def get_results(request_id: str) -> None:
    if request_id not in job_map:
        abort(400, "request_id not found")
    job = job_map[request_id]
    req = request_map[request_id]

    # check status
    status = "QUEUED"
    results = []

    if job.running():
        status = "RUNNING"
    elif job.cancelled():
        status = "CANCELED"
    elif job.done():
        # COMPLETE or FAILED
        if job.exception() is None:
            status = "COMPLETE"
            # TODO: The expected original results are a list of exceptions (or a exception), however here I assume the results are a list of dicts. (which means we need to write a wrapper)
            results = job.result()
        else:
            status = "FAILED"
            results = [{"err_msg": str(job.exception())}]

    response: Response = jsonify({
        "requestId": request_id,
        "request": req,
        "status": status,
        "results": results
    })
    response.status_code = GET_STATUS_CODE

    return response


@app_bp.route("/<string:request_id>/cancel", methods=["POST"])
def cancel_validation(request_id: str) -> None:
    if request_id not in job_map:
        abort(400, "request_id not found")
    job = job_map[request_id]
    try_cancel = job.cancel()
    if not try_cancel:
        abort(400, "Failed to cancel")

    response: Response = jsonify({"request_id": request_id})
    response.status_code = POST_STATUS_CODE
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
        except CrateError as ce:
            # TODO
            pass


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
