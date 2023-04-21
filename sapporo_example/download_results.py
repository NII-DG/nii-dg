#!/usr/bin/env python3
# coding: utf-8

import argparse
import json
from pathlib import Path
from typing import List
from urllib.request import urlopen


def fetch_output_file_list(run_id: str, endpoint: str) -> List[str]:
    with urlopen(f"{endpoint.rstrip('/')}/runs/{run_id}") as response:
        result = json.load(response)
        return [output["file_name"] for output in result["outputs"]]


def download_results(endpoint: str, run_id: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file_list = fetch_output_file_list(run_id, endpoint)

    for output_file in output_file_list:
        with urlopen(f"{endpoint.rstrip('/')}/runs/{run_id}/data/outputs/{output_file}") as response:
            file_path = output_dir.joinpath("outputs").joinpath(output_file).resolve()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(response.read())

    # download run_request.json
    with urlopen(f"{endpoint.rstrip('/')}/runs/{run_id}/data/run_request.json") as response:
        file_path = output_dir.joinpath("run_request.json").resolve()
        with open(file_path, "wb") as f:
            f.write(response.read())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", help="The endpoint to send the request (default: http://localhost:1122)",
                        default="http://localhost:1122", nargs="?")
    parser.add_argument("run_id", help="The RUN_ID of the executed workflow")
    parser.add_argument("output_dir", help="The output directory to save the results (default: ./results)",
                        default="./results", nargs="?")
    args = parser.parse_args()

    download_results(args.endpoint, args.run_id, Path(args.output_dir).resolve())


if __name__ == "__main__":
    main()
