#!/usr/bin/env python3
# coding: utf-8

import argparse
import hashlib
import json
from pathlib import Path

from nii_dg.ro_crate import ROCrate
from nii_dg.schema.sapporo import Dataset, File, SapporoRun


def package_ro_crate(sapporo_endpoint: str, wf_results_dir: Path) -> None:
    ro_crate = ROCrate()
    ro_crate.root["name"] = "example research project"

    outputs_dir_ins = Dataset("outputs/", {"name": "outputs", "hasPart": []})

    with open(wf_results_dir.joinpath("run_request.json"), "r", encoding="utf_8") as f:
        run_req = json.load(f)
        run_req = {key: value for key, value in run_req.items() if value is not None}
        run_req.update(
            {
                "sapporo_location": sapporo_endpoint,
                "state": "COMPLETE",
                "outputs": outputs_dir_ins,
            }
        )

    sapporo_run_ins = SapporoRun(props=run_req)

    for file_path in wf_results_dir.joinpath("outputs").glob("**/*"):
        file_ins = File(
            str(file_path.relative_to(wf_results_dir)), {"name": file_path.name}
        )
        if file_path.suffix != ".html":
            file_ins["contentSize"] = f"{file_path.stat().st_size}B"
            file_ins["sha256"] = hashlib.sha256(file_path.read_bytes()).hexdigest()
        outputs_dir_ins["hasPart"].append(file_ins)
        ro_crate.add(file_ins)

    ro_crate.add(outputs_dir_ins, sapporo_run_ins)
    ro_crate.dump("./ro-crate-metadata.json")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "sapporo_endpoint",
        help="The endpoint of Sapporo, which is as seen from NII-DG server (default: http://sapporo-service:1122)",
        default="http://sapporo-service:1122",
        nargs="?",
    )
    parser.add_argument(
        "wf_results_dir",
        help="The directory where the results of the workflow are stored (default: ./results)",
        default="./results",
        nargs="?",
    )
    args = parser.parse_args()
    package_ro_crate(args.sapporo_endpoint, Path(args.wf_results_dir).resolve())


if __name__ == "__main__":
    main()
