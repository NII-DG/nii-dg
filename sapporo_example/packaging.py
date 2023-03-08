#!/usr/bin/env python3
# coding: utf-8

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

import requests

from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset
from nii_dg.schema.sapporo import File, SapporoRun

ATTRIBUTE = 'filename='
DIR_PATH = Path(__file__).with_name("initial_run")
SAPPORO_ENDPOINT = "http://sapporo-service:1122"


def get_initial_run_id() -> str:
    path = DIR_PATH.joinpath("initial_run.sh")
    proc = subprocess.run(["sh", path], text=True, capture_output=True, check=True)
    req_dict = json.loads(proc.stdout)
    return req_dict["run_id"]


def get_run_status(run_id: str) -> str:
    while True:
        run_status = requests.get(SAPPORO_ENDPOINT + "/runs/" + run_id + "/status", timeout=(10, 30))
        if run_status.json()["state"] not in ["QUEUED", "INITIALIZING", "RUNNING"]:
            break
        time.sleep(30)
    return run_status.json()["state"]


def get_run_results(run_id: str) -> Dict[str, Any]:
    run_result = requests.get(SAPPORO_ENDPOINT + "/runs/" + run_id, timeout=(10, 30))

    return run_result.json()


def download_file(run_id: str, run_dir: Path, file_path: str) -> None:
    run_request = requests.get(SAPPORO_ENDPOINT + "/runs/" + run_id + "/data/" + file_path, timeout=(10, 120))
    save_run_request_path = run_dir.joinpath(file_path)
    with open(save_run_request_path, 'w') as f:
        f.write(run_request.text)


def execute_initial_run() -> str:
    run_id = get_initial_run_id()
    run_state = get_run_status(run_id)

    if run_state not in ["COMPLETE", "EXECUTOR_ERROR"]:
        raise ValueError("Initial execution didn't run successfully.")
    run_results = get_run_results(run_id)

    DIR_PATH.with_name("outputs").mkdir(exist_ok=True)

    file_list = ["outputs/" + file_dict["file_name"] for file_dict in run_results["outputs"]]
    file_list += ["run_request.json", "sapporo_config.json"]

    for file_name in file_list:
        download_file(run_id, DIR_PATH, file_name)

    return run_state


def package() -> None:
    run_state = execute_initial_run()

    ro_crate = ROCrate()
    ro_crate.root["name"] = "example research project"

    with open(DIR_PATH.joinpath("run_request.json"), "r", encoding="utf_8") as f:
        run_req_content = f.read()
    with open(DIR_PATH.joinpath("sapporo_config.json"), "r", encoding="utf_8") as f:
        config_content = f.read()

    run_req = File("run_request.json", {"contents": run_req_content})
    config = File("sapporo_config.json", {"contents": config_content})
    outputs_dir = Dataset("outputs/", {"name": "outputs"})
    sapporo_run = SapporoRun(props={
        "run_request": run_req,
        "sapporo_config": config,
        "state": run_state,
        "outputs": outputs_dir})

    ro_crate.add(run_req, config, outputs_dir, sapporo_run)
    ro_crate.dump(str(DIR_PATH.joinpath("ro-crate-metadata.json")))


if __name__ == "__main__":
    package()
