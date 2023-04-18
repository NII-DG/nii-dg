#!/usr/bin/env python3
# coding: utf-8

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

import requests

from nii_dg.utils import download_file_from_url, get_sapporo_run_status


def get_initial_run_id(sh_path: Path) -> str:
    proc = subprocess.run(["sh", sh_path], text=True, capture_output=True, check=True)
    req_dict = json.loads(proc.stdout)
    return req_dict["run_id"]


def get_run_results(run_id: str, endpoint: str) -> Dict[str, Any]:
    run_result = requests.get(endpoint + "/runs/" + run_id, timeout=(10, 30))

    return run_result.json()


def execute_initial_run(sh_path: Path, run_dir: Path, endpoint: str) -> None:
    run_id = get_initial_run_id(sh_path)
    state = get_sapporo_run_status(run_id, endpoint)

    if state not in ["COMPLETE", "EXECUTOR_ERROR"]:
        raise ValueError("Initial execution didn't run successfully.")
    run_results = get_run_results(run_id, endpoint)

    file_list = ["outputs/" + file_dict["file_name"] for file_dict in run_results["outputs"]]
    file_list += ["run_request.json"]

    for file_name in file_list:
        download_file_from_url(endpoint + "/runs/" + run_id + "/data/" + file_name, run_dir.joinpath(file_name))


if __name__ == "__main__":
    dir_path = Path(__file__).with_name("initial_run_dir")
    sapporo_endpoint = "http://sapporo-service:1122"

    execute_initial_run(Path(__file__).with_name("initial_run.sh"), dir_path, sapporo_endpoint)
