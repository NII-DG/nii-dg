#!/usr/bin/env python3
# coding: utf-8

import sys
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import uuid4

from flask import (Blueprint, Flask, Response, abort, current_app, jsonify,
                   request)

from nii_dg.error import EntityError, GovernanceError
from nii_dg.ro_crate import ROCrate

if TYPE_CHECKING:
    from nii_dg.entity import Entity


GET_STATUS_CODE = 200
POST_STATUS_CODE = 200
JOB_STATUS = [
    "UNKNOWN",
    "QUEUED",
    "RUNNING",
    "COMPLETE",
    "FAILED",
    "EXECUTOR_ERROR",
    "CANCELING",
    "CANCELED",
]


# --- state ---

executor = ThreadPoolExecutor(max_workers=3)
job_map: Dict[str, Future] = {}
request_map: Dict[str, Dict[str, Any]] = {}

# --- result wrapper ---


def result_wrapper(error_dict: List[EntityError]) -> List[Dict[str, str]]:
    result_array = []
    for entity_error in error_dict:
        entity_dict = {}
        entity_dict["entityId"] = entity_error.entity.id
        entity_dict["props"] = entity_error.entity.schema_name + "." + entity_error.entity.type + ":"
        for prop, reason in entity_error.message_dict.items():
            reason_dict = entity_dict.copy()
            reason_dict["props"] += prop
            reason_dict["reason"] = reason
            result_array.append(reason_dict)
    return result_array

# --- controller ---


app_bp = Blueprint("app", __name__)


@ app_bp.errorhandler(400)
def invalid_request(e: Exception) -> Response:
    return jsonify(message=str(e)), 400


@ app_bp.route("/validate", methods=["POST"])
def request_validation() -> Response:
    request_id = str(uuid4())
    request_body = request.json or {}
    entity_ids = request.args.getlist("entityIds", None)

    if request_body == {}:
        # TODO
        return abort(400, "To data governance, ro-crate-metadata.json is required as a request body.")

    try:
        crate = ROCrate(request_body)
    except Exception:
        # TODO: exceptionの種類確認
        abort(400, "Invalid ro-crate.")

    target_entities: List[Entity] = []
    if entity_ids:
        for entity_id in entity_ids:
            target_entities.extend(crate.get_by_id(entity_id))
            if len(crate.get_by_id(entity_id)) == 0:
                abort(400, f"Invalid entityId: {entity_id} is not found in the crate.")

    job = executor.submit(validate, crate, target_entities)

    with current_app.app_context():
        request_map[request_id] = {
            "roCrate": request_body,
            "entityIds": entity_ids}
        job_map[request_id] = job

    response: Response = jsonify({"request_id": request_id})
    response.status_code = POST_STATUS_CODE
    return response


@ app_bp.route("/<string:request_id>", methods=["GET"])
def get_results(request_id: str) -> None:
    if request_id not in job_map:
        abort(400, f"Request_id {request_id} is not found.")
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
            results = job.result()
        elif isinstance(job.exception(), GovernanceError):
            status = "FAILED"
            results = result_wrapper(job.exception().entity_errors)  # type:ignore
        else:
            status = "EXECUTOR_ERROR"
            results = [{"err_msg": str(job.exception())}]

    response: Response = jsonify({
        "requestId": request_id,
        "request": req,
        "status": status,
        "results": results
    })
    response.status_code = GET_STATUS_CODE

    return response


@ app_bp.route("/<string:request_id>/cancel", methods=["POST"])
def cancel_validation(request_id: str) -> None:
    if request_id not in job_map:
        abort(400, f"Request_id {request_id} is not found.")
    job = job_map[request_id]
    try_cancel = job.cancel()
    if not try_cancel:
        abort(400, "Failed to cancel")

    response: Response = jsonify({"request_id": request_id})
    response.status_code = POST_STATUS_CODE
    return response


@ app_bp.route('/healthcheck', methods=['GET'])
def check_health() -> Response:
    return Response(jsonify({"message": "OK"}), status=GET_STATUS_CODE)


# --- job ---


def validate(crate: ROCrate, entities: List["Entity"]) -> List[Any]:
    if len(entities) > 0:
        governance_error = GovernanceError()
        for entity in entities:
            try:
                entity.validate(crate)
            except EntityError as err:
                governance_error.add_error(err)

        if len(governance_error.entity_errors) > 0:
            raise governance_error
    else:
        crate.validate()
    return []

# --- app ---


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(app_bp)

    return app


def main(env: Optional[str]) -> None:
    app = create_app()

    # for development
    if env == "dev":
        app.config["DEBUG"] = True
        app.config["TESTING"] = True
    elif env:
        raise ValueError(f"Invalid argument: {env}")

    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    env = None
    if len(sys.argv) > 1:
        env = sys.argv[1]
    main(env)
