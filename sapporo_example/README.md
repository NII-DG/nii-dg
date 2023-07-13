# Governance Case using NII-DG and Sapporo

This document provides a step-by-step guide on using the NII-DG library to package the results of a workflow executed by Sapporo as an RO-Crate. For more information on Sapporo, refer to the GitHub repository at [sapporo-wes/sapporo-service](https://github.com/sapporo-wes/sapporo-service).

## Preparations

- We will package the workflow execution results from Sapporo as research data to generate a RO-Crate.
- Sapporo and the NII-DG REST API server will be launched as Docker containers, connected on the same network.
- We will perform a validation that checks:
  1. The workflow is re-executable based on the values in the RO-Crate.
  2. The status of the re-execution matches the status stated in the RO-Crate.
  3. The size and checksum of the result files obtained from re-execution match the values in the RO-Crate (if recorded in the RO-Crate).

## Step 1: Launch Sapporo and the NII-DG REST API Server

```bash
# In the sapporo_example directory
$ docker compose up -d
[+] Running 2/2
 ✔ Container sapporo-service  Running                                                                0.0s
 ✔ Container nii-dg           Started                                                                0.9s
$ docker compose ps
NAME                IMAGE                                       COMMAND                  SERVICE             CREATED              STATUS              PORTS
nii-dg              nii-dg                                      "tini -- python /app…"   nii-dg              12 seconds ago       Up 11 seconds       0.0.0.0:5000->5000/tcp
sapporo-service     ghcr.io/sapporo-wes/sapporo-service:1.4.9   "tini -- uwsgi --yam…"   sapporo-service     About a minute ago   Up About a minute   0.0.0.0:1122->1122/tcp
```

As a communication check:

```bash
# Host -> Sapporo
$ curl localhost:1122/service-info
{
  "auth_instructions_url"...
}

# Host -> NII-DG REST API Server
$ curl localhost:5000/healthcheck
{"message":"OK"}

# NII-DG REST API Server -> Sapporo
$ docker compose exec nii-dg bash
# In container
$ apt update
$ apt install -y curl
$ curl sapporo-service:1122/service-info
{
  "auth_instructions_url"...
}
```

## Step 2: Install the NII-DG Library

The NII-DG container launched in the previous step is for validation. In this step, we'll install the NII-DG library for packaging.

```bash
# Move to root directory
$ cd ../
$ ls setup.py
setup.py
$ python3 -m pip install .
...
$ python3 -m pip list | grep nii-dg
nii-dg                 1.0.0
```

## Step 3: Execute a Workflow in Sapporo (`execute_workflow.py`)

We will use the workflow [trimming_and_qc.cwl](https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/trimming_and_qc.cwl) as the workflow to be executed by Sapporo. This workflow is written in CommonWorkflowLanguage (CWL) and performs QC using FASTQC and trimming using Trimmomatic on FASTQ files (nucleotide sequence files) as input.

en: To execute the workflow using `curl`, use the following command (you can skip the command below):

```bash
$ curl -X POST \
     -F 'workflow_params={"fastq_1":{"location":"ERR034597_1.small.fq.gz","class":"File"},"fastq_2":{"location":"ERR034597_2.small.fq.gz","class":"File"},"nthreads":2}' \
     -F 'workflow_type=CWL' \
     -F 'workflow_type_version=v1.0' \
     -F 'workflow_url=https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/trimming_and_qc.cwl' \
     -F 'workflow_engine_name=cwltool' \
     -F 'workflow_attachment=[{"file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_2.small.fq.gz","file_name": "ERR034597_2.small.fq.gz"},{"file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_1.small.fq.gz","file_name": "ERR034597_1.small.fq.gz"}]' \
     http://localhost:1122/runs
{"run_id": "d45a404e-8d8a-43ac-bbf8-b686ee426062"}
```

The `execute_workflow.py` script is an implementation of this command in Python, and is used to execute the workflow.

```bash
$ python3 execute_workflow.py -h
usage: execute_workflow.py [-h] [endpoint]

positional arguments:
  endpoint    The endpoint to send the request (default: http://localhost:1122)

optional arguments:
  -h, --help  show this help message and exit

$ python3 execute_workflow.py http://localhost:1122
{"run_id": "d45a404e-8d8a-43ac-bbf8-b686ee426062"}
```

The `RUN_ID` in Sapporo is `d45a404e-8d8a-43ac-bbf8-b686ee426062` as output. To check the status of the run in Sapporo, use this `RUN_ID`.
(The original source of the run status is located in `${PWD}/run`.)

```bash
$ curl localhost:1122/runs/d45a404e-8d8a-43ac-bbf8-b686ee426062 | jq .state
"COMPLETE"
```

Once the state is `COMPLETE`, proceed to the next step.

## Step 4: Retrieve the Workflow Execution Results from Sapporo (`download_results.py`)

Sapporo is expected to be deployed as a REST API Server in a cloud instance. Therefore, it is necessary to download the execution results (e.g., output files, etc.) from Sapporo.

The `download_results.py` script is provided as a script for this purpose.

```bash
$ python3 download_results.py -h
usage: download_results.py [-h] [endpoint] run_id [output_dir]

positional arguments:
  endpoint    The endpoint to send the request (default: http://localhost:1122)
  run_id      The RUN_ID of the executed workflow
  output_dir  The output directory to save the results (default: ./results)

optional arguments:
  -h, --help  show this help message and exit

$ python3 download_results.py http://localhost:1122 d45a404e-8d8a-43ac-bbf8-b686ee426062 ./results

$ tree results/
results/
├── outputs
│   ├── ERR034597_1.small_fastqc.html
│   ├── ERR034597_1.small.fq.trimmed.1P.fq
│   ├── ERR034597_1.small.fq.trimmed.1U.fq
│   ├── ERR034597_1.small.fq.trimmed.2P.fq
│   ├── ERR034597_1.small.fq.trimmed.2U.fq
│   └── ERR034597_2.small_fastqc.html
└── run_request.json

1 directory, 7 files
```

The results are downloaded to `./results`.

## Step 5: Generate a RO-Crate with NII-DG (`package_ro_crate.py`)

Using the NII-DG library, package the results downloaded in the previous step as an RO-Crate.

```bash
$ python3 package_ro_crate.py -h
usage: package_ro_crate.py [-h] [sapporo_endpoint] [wf_results_dir]

positional arguments:
  sapporo_endpoint  The endpoint of Sapporo, which is as seen from NII-DG server
                    (default: http://sapporo-service:1122)
  wf_results_dir    The directory where the results of the workflow are stored
                    (default: ./results)

optional arguments:
  -h, --help        show this help message and exit

$ python3 package_ro_crate.py

$ ls ro-crate-metadata.json
ro-crate-metadata.json
$ head ro-crate-metadata.json
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    {
      "@id": "./",
      "@type": "Dataset",
      "hasPart": [
        {
          "@id": "outputs/ERR034597_1.small.fq.trimmed.2U.fq"
        },
```

## Step 6: Validate the RO-Crate with NII-DG API Server

Details of the NII-DG API Server can be found at [api-quick-start.md](../api-quick-start.md).
From `Step 1: Launch Sapporo and the NII-DG REST API Server`, the NII-DG API Server is running at `localhost:5000`.

```bash
$ curl localhost:5000/healthcheck
{"message": "OK"}
```

POST the generated `ro-crate-metadata.json` to `/validate` as follows.:

```bash
$ curl -X POST -H "Content-Type: application/json" -d @./ro-crate-metadata.json http://localhost:5000/validate
{"request_id":"bd6f18a4-1599-41d2-bcbd-75f2cda2209d"}
```

The response will return a `request_id`.

Use this `request_id` to GET `/{request_id}` and retrieve the validation results.

```bash
$ curl localhost:5000/bd6f18a4-1599-41d2-bcbd-75f2cda2209d
{
  "request": {
    "entityIds": [],
    "roCrate": {
      "@context": "https://w3id.org/ro/crate/1.1/context",
      "@graph": [
        {
          ...
        }
      ]
    }
  },
  "requestId": "bd6f18a4-1599-41d2-bcbd-75f2cda2209d",
  "results": [],
  "status": "COMPLETE"
}
```

Since there were no problems with the validation, `status` is `COMPLETE` and `results` is an empty list.

---

As an example of a problem with the validation (e.g., the output file name does not match), edit `./ro-crate-metadata.json`.

```bash
$ cp ./ro-crate-metadata.json ./ro-crate-metadata_failed.json
$ sed -i 's/ERR034597_1.small_fastqc.html/ERR034597_1.small_fastqc_failed.html/' ./ro-crate-metadata_failed.json
$ diff -u ./ro-crate-metadata.json ./ro-crate-metadata_failed.json
```

Use the edited RO-Crate `ro-crate-metadata_failed.json` to perform the validation.

```bash
$ curl -X POST -H "Content-Type: application/json" -d @./ro-crate-metadata_failed.json http://localhost:5000/validate
{"request_id":"32012249-d8f7-4f64-b20d-853ea5be67b5"}

$ curl localhost:5000/32012249-d8f7-4f64-b20d-853ea5be67b5
{
  "request": {
    "entityIds": [],
    "roCrate": {
      "@context": "https://w3id.org/ro/crate/1.1/context",
      "@graph": [
        {
          ...
        }
      ]
    }
  },
  "requestId": "32012249-d8f7-4f64-b20d-853ea5be67b5",
  "results": [
    {
      "entityId": "#sapporo-run",
      "props": "sapporo.SapporoRun:outputs",
      "reason": "The file ERR034597_1.small_fastqc.html is included in the result of re-execution, but this crate does not have File entity with @id ERR034597_1.small_fastqc.html."
    }
  ],
  "status": "FAILED"
}
```

Since there was a problem with the validation, `status` is `FAILED` and `results` indicates that there is a problem.
