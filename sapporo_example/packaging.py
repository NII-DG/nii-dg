#!/usr/bin/env python3
# coding: utf-8

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict

import requests

from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset
from nii_dg.schema.sapporo import File, SapporoRun
from nii_dg.utils import (download_file_from_url, generate_run_request_json,
                          get_file_sha256, get_sapporo_run_status)

ATTRIBUTE = 'filename='


def get_initial_run_id(sh_path: Path) -> str:
    proc = subprocess.run(["sh", sh_path], text=True, capture_output=True, check=True)
    req_dict = json.loads(proc.stdout)
    return req_dict["run_id"]


def get_run_results(run_id: str, endpoint: str) -> Dict[str, Any]:
    run_result = requests.get(endpoint + "/runs/" + run_id, timeout=(10, 30))

    return run_result.json()


def execute_initial_run(sh_path: Path, run_dir: Path, endpoint: str) -> str:
    run_id = get_initial_run_id(sh_path)
    state = get_sapporo_run_status(run_id, endpoint)

    if state not in ["COMPLETE", "EXECUTOR_ERROR"]:
        raise ValueError("Initial execution didn't run successfully.")
    run_results = get_run_results(run_id, endpoint)

    file_list = ["outputs/" + file_dict["file_name"] for file_dict in run_results["outputs"]]
    file_list += ["run_request.json"]

    for file_name in file_list:
        download_file_from_url(endpoint + "/runs/" + run_id + "/data/" + file_name, run_dir.joinpath(file_name))

    return run_state


def package(state: str, run_dir: Path, endpoint: str) -> None:
    ro_crate = ROCrate()
    ro_crate.root["name"] = "example research project"
    outputs_dir = Dataset("outputs/", {"name": "outputs"})

    with open(run_dir.joinpath("run_request.json"), "r", encoding="utf_8") as f:
        run_req = json.load(f)
    run_req_content = {key: str(value) for key, value in run_req.items() if value is not None}
    run_req_content.update({
        "sapporo_location": endpoint,
        "state": state,
        "outputs": outputs_dir})

    sapporo_run = SapporoRun(props=run_req_content)

    outputs_iter = run_dir.joinpath("outputs").iterdir()
    for file_path in outputs_iter:
        file = File(str(file_path.relative_to(run_dir)))
        file["contentSize"] = str(os.path.getsize(file_path)) + "B"
        if not str(file_path).endswith("html"):
            file["sha256"] = get_file_sha256(file_path)
        ro_crate.add(file)

    ro_crate.add(outputs_dir, sapporo_run)
    ro_crate.dump(str(run_dir.joinpath("ro-crate-metadata.json")))


if __name__ == "__main__":
    dir_path = Path(__file__).with_name("initial_run")
    sapporo_endpoint = "http://sapporo-service:1122"

    # run_state = execute_initial_run(dir_path.joinpath("initial_run.sh"), dir_path, sapporo_endpoint)
    run_state = "COMPLETE"

    package(run_state, dir_path, sapporo_endpoint)
