#!/usr/bin/env python3
# coding: utf-8

import json
import os
import sys
from pathlib import Path

from nii_dg.ro_crate import ROCrate
from nii_dg.schema.sapporo import Dataset, File, SapporoRun
from nii_dg.utils import get_file_sha256


def package(state: str, run_dir: Path, endpoint: str, validate_pattern: str = "complete") -> None:
    ro_crate = ROCrate()
    ro_crate.root["name"] = "example research project"
    outputs_dir = Dataset("outputs/", {"name": "outputs", "hasPart": []})

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
        file = File(str(file_path.relative_to(run_dir)), {"name": file_path.name})
        outputs_dir["hasPart"].append(file)

        if validate_pattern == "complete" and str(file_path).endswith("html"):
            pass
        else:
            file["contentSize"] = str(os.path.getsize(file_path)) + "B"
            file["sha256"] = get_file_sha256(file_path)

        ro_crate.add(file)

    ro_crate.add(outputs_dir, sapporo_run)
    ro_crate.dump(str(run_dir.parent.joinpath(validate_pattern, "ro-crate-metadata.json")))


if __name__ == "__main__":
    dir_path = Path(__file__).with_name("initial_run_dir")
    sapporo_endpoint = "http://sapporo-service:1122"
    run_state = "COMPLETE"

    package(run_state, dir_path, sapporo_endpoint, sys.argv[1])
