## Deploy NII-DG API Server

Clone this Github repository.

Then run docker-compose up to launch the server:

```bash
$ docker compose -f compose.api.yml up
Attaching to nii-dg
nii-dg  | INFO:waitress:Serving on http://0.0.0.0:5000
```

Server launched successfully and accessible at the address `localhost:5000`.

To check if the server is working, use the endpoint `/healthcheck`.
You get `OK` in the message from running server.

```bash
$ curl localhost:5000/healthcheck
{"message":"OK"}
```

## Request RO-Crate validation to the server

### Prepare ro-crate-metadata.json

You need `ro-crate-metadata.json`, RO-Crate json file created by using NII-DG library.
Data governance is performed based on the RO-Crate as an input.

### POST /validate

Access the POST endpoint `/validate` with your RO-Crate as a request body to request governance.

```bash
$ curl -X POST localhost:5000/validate -H "Content-Type: application/json" -d @path/to/ro-crate-metadata
{"request_id":"a84d2318-8b57-49c4-848d-b1935e4a1224"}
```

Several RO-Crates are prepared for testing under [./tests/examples](./tests/examples); so use `example_complete.json` as follows:

```bash
$ curl -X POST localhost:5000/validate -H "Content-Type: application/json" -d @./tests/examples/example_complete.json
{"request_id":"e502a052-d261-4795-8fef-22ee66cf07cd"}
```

You get `request_id` in uuid4 when your request is successfully applied to the server.

In the case your ro-crate is in wrong format, governance request is denied.

```bash
$ curl -X POST localhost:5000/validate -H "Content-Type: application/json" -d @path/to/wrong-ro-crate
{
  "message": "400 Bad Request: RO-Crate has invalid property."
}
```

### Governance with only specified entities

If you want to limit the entities to be governed for reasons such as time-consuming verification, you can specify the target entities by sending entity ID as a query parameter `entityIds`.
Please make sure that the entity id is percent-encoded format and the URI is enclosed with single/double quotes.

```bash
$ curl -X POST "localhost:5000/validate?entityIds=file_1.txt&entityIds=https%3A%2F%2Fexample.com%2Fperson" -H "Content-Type: application/json" -d @path/to/ro-crate-metadata
{"request_id":"bd453ed1-30b9-4873-b240-e459467ea9dc"}
```

## Get Governance Result

You can get the status of the governance by using the request_id.
The status `COMPLETE` means the governance check finished successfully and no problem is found. The `results` value is empty list.
The status `FAILED` also means the governance check finished successfully, but found the problems. The `results` value is problem list of dictionaries consisting of entity ID, property and list of failed reasons.

```bash
$ curl localhost:5000/a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc
{
  "request": {
    "entityIds": [],
    "roCrate": {
      ...,
    }
  },
  "requestId": "a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc",
  "results": [
    {
      "entityId": "https://example.com/person",
      "props": "cao.Person:@id",
      "reason": ["Unable to access https://example.com/person due to 404 Client Error: Not Found for url: https://example.com/person"]
    },
    {
      "entityId": "#ginmonitoring",
      "props": "ginfork.GinMonitoring:datasetStructure",
      "reason": ["Couldn't find required directories: named ['source', 'input_data', 'output_data']."]
    }
  ],
  "status": "FAILED"
}
```

When you specified entities, `request` property has target list.

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
      "reason": ["Unable to access https://example.com/person due to 404 Client Error: Not Found for url: https://example.com/person"]
    }
  ],
  "status": "FAILED"
}
```

## POST Cancel Governance Request

Only when your request is in statue `QUEUED`, you can cancel it. If the request successfully canceled, its status id changed to `CANCELED`.

When cancel request is successfully applied, you get your request ID.

```bash
$ curl localhost:5000/a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc/cancel -X POST
{"request_id": "a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc"}
```

After a moment:

```bash
$ curl localhost:5000/a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc
{
  ...,
  "request_id": "a2216a8d-a9d1-4aa3-ab01-1dc0e7c85ccc",
  "results":[],
  "status":"CANCELED"}
```
