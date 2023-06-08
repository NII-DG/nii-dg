#!/usr/bin/env python3
# coding: utf-8

import logging
import os
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from copy import deepcopy
from queue import Empty, Queue
from time import sleep
from typing import TYPE_CHECKING, Any, Dict, List
from uuid import uuid4

from flask import Blueprint, Flask, Response, abort, jsonify, request
from waitress import serve

from nii_dg.error import CrateError, CrateValidationError, EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.utils import DG_CONFIG

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
job_queue = Queue()  # type:ignore
job_map: Dict[str, Future] = {}  # type:ignore
request_map: Dict[str, Dict[str, Any]] = {}

# --- result wrapper ---


def result_wrapper(error_list: List[EntityError]) -> List[Dict[str, str]]:
    result_array = []
    for entity_error in error_list:
        entity_dict = {}
        entity_dict["entityId"] = entity_error.entity.id
        entity_dict["props"] = (
            entity_error.entity.schema_name + "." + entity_error.entity.type + ":"
        )  # type:ignore
        for prop, reason in entity_error.errors.items():
            reason_dict = entity_dict.copy()
            reason_dict["props"] += prop
            reason_dict["reason"] = reason
            result_array.append(reason_dict)
    return result_array


# --- controller ---


app_bp = Blueprint("app", __name__)


@app_bp.errorhandler(400)
def invalid_request(err: Exception) -> Response:
    response: Response = jsonify(message=str(err))
    response.status_code = 400
    return response


@app_bp.errorhandler(500)
def internal_error(err: Exception) -> Response:
    response: Response = jsonify(message="An internal error occurred.")
    response.status_code = 500
    return response


def validate(crate: ROCrate, entities: List["Entity"]) -> List[Any]:
    if len(entities) > 0:
        error = CrateValidationError()
        for entity in entities:
            try:
                entity.validate(crate)
            except EntityError as err:
                error.add(err)

        if error.has_error():
            raise error
    else:
        crate.validate()
    return []


@app_bp.route("/validate", methods=["POST"])
def request_validation() -> Response:
    request_id = str(uuid4())
    try:
        request_body = request.json
    except Exception:
        abort(400, "RO-Crate json file is not found in the request.")
    entity_ids: List[str] = request.args.getlist("entityIds", None)

    try:
        crate = ROCrate(deepcopy(request_body))
        crate.as_jsonld()
    except CrateError as crateerr:
        abort(400, crateerr)

    target_entities: List[Entity] = []
    if entity_ids:
        for entity_id in entity_ids:
            target_entities.extend(crate.get_by_id(entity_id))
            if len(crate.get_by_id(entity_id)) == 0:
                abort(400, f"Entity ID `{entity_id}` is not found in the crate.")

    # add job to queue along with the request_id
    job_queue.put((request_id, validate, crate, target_entities))

    request_map[request_id] = {"roCrate": request_body, "entityIds": entity_ids}

    response: Response = jsonify({"request_id": request_id})
    response.status_code = POST_STATUS_CODE
    return response


@app_bp.route("/<string:request_id>", methods=["GET"])
def get_results(request_id: str) -> Response:
    if request_id not in request_map:
        abort(400, f"Request ID `{request_id}` is not found.")

    req = request_map[request_id]

    # get job future if it exists
    job = job_map.get(request_id, None)

    # check status
    status = "QUEUED"
    results = []

    if job is not None:
        if job.running():
            status = "RUNNING"
        elif job.cancelled():
            status = "CANCELED"
        elif job.done():
            # COMPLETE or FAILED
            try:
                results = job.result()  # Get the result or exception
                status = "COMPLETE"
            except CrateValidationError as err:
                status = "FAILED"
                results = result_wrapper(err.errors)
            except Exception as exc:
                status = "EXECUTOR_ERROR"
                results = [{"err_msg": str(exc)}]

    response: Response = jsonify(
        {"requestId": request_id, "request": req, "status": status, "results": results}
    )
    response.status_code = GET_STATUS_CODE

    return response


@app_bp.route("/<string:request_id>/cancel", methods=["POST"])
def cancel_validation(request_id: str) -> Response:
    if request_id not in job_map:
        abort(400, f"Request ID `{request_id}` is not found.")
    job = job_map[request_id]
    try_cancel = job.cancel()
    if not try_cancel:
        abort(400, "Failed to cancel")

    response: Response = jsonify({"request_id": request_id})
    response.status_code = POST_STATUS_CODE
    return response


@app_bp.route("/healthcheck", methods=["GET"])
def check_health() -> Response:
    response: Response = jsonify({"message": "OK"})
    response.status_code = GET_STATUS_CODE
    return response


# --- job ---

def process_jobs() -> None:
    while True:
        sleep(0.1)  # wait for 0.1 second
        try:
            job = job_queue.get(timeout=1)  # wait for a job for 1 second
            request_id, job_func, *job_args = job
            future = executor.submit(job_func, *job_args)  # submit the job to the executor
            job_map[request_id] = future  # store the future
        except Empty:
            pass  # no job was available


# Start processing jobs
threading.Thread(target=process_jobs, daemon=True).start()

# --- app ---


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(app_bp)
    logging.basicConfig(level=logging.INFO)
    return app


def main() -> None:
    app = create_app()

    if os.getenv("DG_WSGI_SERVER") == "waitress":
        import logging

        waitress_logger = logging.getLogger("waitress")
        waitress_logger.setLevel(logging.INFO)
        serve(
            app,
            host=DG_CONFIG["DG_HOST"],
            port=DG_CONFIG["DG_PORT"],
            threads=DG_CONFIG["DG_WSGI_THREADS"],
        )
    else:
        # for debug
        app.config["FLASK_ENV"] = "development"
        app.config["DEBUG"] = True
        app.config["TESTING"] = True
        app.run(host=DG_CONFIG["DG_HOST"], port=DG_CONFIG["DG_PORT"])


if __name__ == "__main__":
    main()
