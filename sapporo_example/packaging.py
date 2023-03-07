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


def get_initial_run_id() -> str:
    path = Path(__file__).with_name("initial_run.sh")
    proc = subprocess.run(["sh", path], text=True, capture_output=True, check=True)
    req_dict = json.loads(proc.stdout)
    return req_dict["run_id"]


def get_run_status(run_id: str) -> str:
    while True:
        run_status = requests.get("http://localhost:1122/runs/" + run_id + "/status")
        if run_status.json()["state"] not in ["QUEUED", "INITIALIZING", "RUNNING"]:
            break
        time.sleep(30)
    return run_status.json()["state"]


def get_run_results(run_id: str) -> Dict[str, Any]:
    run_result = requests.get("http://localhost:1122/runs/" + run_id)

    return run_result.json()


def get_output_file(url: str, run_dir: Path) -> None:
    output_file = requests.get(url)
    contentDisposition = output_file.headers['Content-Disposition']
    filename = contentDisposition[contentDisposition.find(ATTRIBUTE) + len(ATTRIBUTE):]

    save_file_path = run_dir.joinpath(filename)
    with open(save_file_path, 'w') as save_file:
        save_file.write(output_file.text)


def download_file(run_id: str, run_dir: Path, file_path: str) -> None:
    run_request = requests.get("http://localhost:1122/runs/" + run_id + "/data/" + file_path)
    save_run_request_path = run_dir.joinpath(file_path)
    with open(save_run_request_path, 'w') as f:
        f.write(run_request.text)


def save_run_results(run_id: str) -> None:
    if get_run_status(run_id) != "COMPLETE":
        return
    run_dir = Path(__file__).with_name(run_id)
    run_dir.mkdir(exist_ok=True)
    run_results = get_run_results(run_id)
    for file in run_results["outputs"]:
        get_output_file(file["file_url"], run_dir)
    get_json_files(run_id, run_dir, "run_request.json")
    get_json_files(run_id, run_dir, "sapporo_config.json")


def do_initial_run() -> None:
    run_id = get_initial_run_id()
    run_state = get_run_status(run_id)
    if run_state != "COMPLETE":
        raise ValueError("Initial execution didn't run successfully.")
    run_results = get_run_results(run_id)

    run_dir = Path(__file__)
    run_dir.with_name("outputs").mkdir(exist_ok=True)

    file_list = ["outputs/" + file_dict["file_name"] for file_dict in run_results["outputs"]]
    file_list += ["run_request.json", "sapporo_config.json"]

    for file_name in file_list:
        download_file(run_id, run_dir, file_name)


def package() -> None:
    ro_crate = ROCrate()
    ro_crate.root["name"] = "example research project"

    run_req = File("outputs/run_request.json")
    config = File("outputs/sapporo_config.json")
    outputs_dir = Dataset("outputs", {"name": "outputs", "description": "Set of output files of workflow run"})
    sapporo_run = SapporoRun(props={
        "run_request": run_req,
        "sapporo_config": config,
        "states": "COMPLETE",
        "outputs": outputs_dir})

    ro_crate.add(run_req, config, outputs_dir, sapporo_run)

    print(json.dumps(ro_crate.as_jsonld(), indent=2))


if __name__ == "__main__":
    package()
