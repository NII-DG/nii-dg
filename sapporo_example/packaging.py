#!/usr/bin/env python3
# coding: utf-8

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

import requests

ATTRIBUTE = 'filename='


def get_initial_run_id() -> str:
    path = Path(__file__).with_name("base.sh")
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

    save_file_path = Path.joinpath(run_dir, filename)
    with open(save_file_path, 'wb') as save_file:
        save_file.write(output_file.content)


def save_run_request(run_result: Dict[str, Any]) -> None:
    SAVE_DIR = os.getcwd() + "/sapporo_example/test"
    save_run_request_path = Path.joinpath(SAVE_DIR + "/run_request.json")
    with open(save_run_request_path, 'w') as f:
        json.dump(run_result["request"], f, indent=4)


def main() -> None:
    run_id = get_initial_run_id()
    if get_run_status(run_id) != "COMPLETE":
        return
    run_dir = Path(__file__).with_name(run_id)
    run_dir.mkdir(exist_ok=True)


if __name__ == "__main__":
    main()
