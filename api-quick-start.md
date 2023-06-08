# Quick Start Guide for NII-DG API Server

## Setting Up the NII-DG API Server

To deploy the API server, start by cloning this Github repository or downloading the source code from the [releases page](https://github.com/NII-DG/nii-dg/releases). Once you have the source code, you can initiate the server by executing the following command:

```bash
$ docker compose -f compose.api.yml up -d
[+] Running 10/10
 ✔ app 9 layers [⣿⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                            4.9s
   ✔ 6eab20599fab Already exists                                              0.0s
   ✔ f790e9177a85 Already exists                                              0.0s
   ✔ 6dbe8744009a Already exists                                              0.0s
   ✔ 176e3d22ecf5 Already exists                                              0.0s
   ✔ 0e85dc1c893f Already exists                                              0.0s
   ✔ 9989f65613d8 Pull complete                                               0.7s
   ✔ b06a617fc75b Pull complete                                               3.2s
   ✔ d6616e9627d9 Pull complete                                               3.2s
   ✔ 5e28fee49148 Pull complete                                               3.3s
[+] Building 0.0s (0/0)
[+] Running 2/2
 ✔ Network nii-dg_default  Created                                            0.1s
 ✔ Container nii-dg        Started                                            1.0s
```

Upon successful execution, the server will be operational and accessible at localhost:5000. The following message indicates a successful launch:

```bash
$ docker compose -f compose.api.yml logs app
nii-dg  | INFO:waitress:Serving on http://0.0.0.0:5000
```

To ensure the server is functioning as expected, access the /healthcheck endpoint. A successful check will yield the message OK.

```bash
$ curl localhost:5000/healthcheck
{"message":"OK"}
```

## Validating RO-Crate with the Server

### Setting Up ro-crate-metadata.json

A JSON file named ro-crate-metadata.json is needed to perform data governance. This file is an RO-Crate JSON file generated using the NII-DG library, and it forms the basis of the input data for validation.

### Using POST /validate Endpoint

You can request data governance by submitting your RO-Crate data to the /validate endpoint via a POST request.

```bash
$ curl -X POST localhost:5000/validate -H "Content-Type: application/json" -d @path/to/ro-crate-metadata
{"request_id":"a84d2318-8b57-49c4-848d-b1935e4a1224"}
```

For testing purposes, several RO-Crates are provided in the [./tests/example](./tests/example) directory. To use [`./tests/example/sample_crate.json`](./tests/example/sample_crate.json), perform the following:

```bash
$ curl -X POST localhost:5000/validate -H "Content-Type: application/json" -d @./tests/example/sample_crate.json
{"request_id":"e141c2a2-317d-44c3-bdae-c0683d1c6d88"}
```

Upon a successful request, the server responds with a request_id in uuid4 format. If your RO-Crate data is not in the correct format, the governance request will be rejected.

```bash
$ curl -X POST localhost:5000/validate -H "Content-Type: application/json" -d @path/to/wrong-ro-crate
{
  "message": "400 Bad Request: RO-Crate has invalid property."
}
```

### Specifying Entities for Governance

If you wish to limit the entities for governance (perhaps due to lengthy verification times), you can specify the target entities by appending the entityIds query parameter. Ensure that the entity ID is percent-encoded and the URI is enclosed in single/double quotes.

```bash
$ curl -X POST "localhost:5000/validate?entityIds=file_1.txt&entityIds=https%3A%2F%2Fexample.com%2Fperson" -H "Content-Type: application/json" -d @path/to/ro-crate-metadata
{"request_id":"bd453ed1-30b9-4873-b240-e459467ea9dc"}
```

## Retrieving Governance Results

You can check the status of governance using the provided `request_id`. A `COMPLETE` status indicates successful completion of the governance check without any issues, and the `results` field will be an empty list. A `FAILED` status indicates that the check was completed but problems were discovered, and the `results` field will contain a list of dictionaries detailing the problematic entity ID, property, and the reason for failure.

```bash
$ curl -s localhost:5000/e141c2a2-317d-44c3-bdae-c0683d1c6d88 | jq .
{
  "request": {
    "entityIds": [],
    "roCrate": {
      "@context": "https://w3id.org/ro/crate/1.1/context",
      "@graph": [
        ...
      ]
    }
  },
  "requestId": "e141c2a2-317d-44c3-bdae-c0683d1c6d88",
  "results": [],
  "status": "COMPLETE"
}
```

When specific entities were targeted, the `request` property will contain a list of the targeted entities.

```bash
$ curl localhost:5000/bd453ed1-30b9-4873-b240-e459467ea9dc
{
  "request":
   {
    "entityIds": [
      "file_1.txt",
      "https://example.com/person"
    ],
  ...,
  },
  "requestId": "bd453ed1-30b9-4873-b240-e459467ea9dc",
  "results": [
    {
      "entityId": "https://example.com/person",
      "props": "cao.Person:@id",
      "reason": "Unable to access https://example.com/person due to 404 Client Error: Not Found for url: https://example.com/person"
    }
  ],
  "status": "FAILED"
}
```

## Cancelling Governance Request via POST

You can cancel your governance request only if its status is `QUEUED`. Upon successful cancellation, the request status changes to `CANCELED` and the server responds with your request ID.

```bash
$ $ curl localhost:5000/a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc/cancel -X POST
{"request_id": "a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc"}
```

After a brief period:

```bash
$ curl localhost:5000/a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc
{
  ...,
  "request_id": "a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc",
  "results":[],
  "status":"CANCELED"}
```

This concludes the quick start guide for setting up and using the NII-DG API Server.
