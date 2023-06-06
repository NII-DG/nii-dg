#!/usr/bin/env python3
# coding: utf-8

import argparse
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def execute_workflow(endpoint: str) -> None:
    data = {
        "workflow_params": json.dumps(
            {
                "fastq_1": {"location": "ERR034597_1.small.fq.gz", "class": "File"},
                "fastq_2": {"location": "ERR034597_2.small.fq.gz", "class": "File"},
                "nthreads": 2,
            }
        ),
        "workflow_type": "CWL",
        "workflow_type_version": "v1.0",
        "workflow_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/trimming_and_qc.cwl",
        "workflow_engine_name": "cwltool",
        "workflow_attachment": json.dumps(
            [
                {
                    "file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_2.small.fq.gz",
                    "file_name": "ERR034597_2.small.fq.gz",
                },
                {
                    "file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_1.small.fq.gz",
                    "file_name": "ERR034597_1.small.fq.gz",
                },
            ]
        ),
    }

    data = urlencode(data).encode("utf-8")  # type: ignore
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # remove trailing slash from endpoint
    request = Request(f"{endpoint.rstrip('/')}/runs", data=data, headers=headers)  # type: ignore

    with urlopen(request) as response:
        result = json.load(response)
        print(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "endpoint",
        help="The endpoint to send the request (default: http://localhost:1122)",
        default="http://localhost:1122",
        nargs="?",
    )
    args = parser.parse_args()
    execute_workflow(args.endpoint)


if __name__ == "__main__":
    main()
