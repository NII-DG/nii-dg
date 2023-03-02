## Deploy NII-DG API Server
Clone this Github repository

Then run docker-compose up to launch the server:

```
$docker compose -f compose.api.yml up
Attaching to nii-dg
```
Server launched successfully and accessible at the address `localhost:5000`.

To check if the server is working, use the endpoint `/healthcheck`. You get `OK` in the message from running server.
```
$ curl localhost:5000/healthcheck
{"message":"OK"}
```

## Request RO-Crate validation to the server
### Prepare ro-crate-metadata.json
You need `ro-crate-metadata.json`, RO-Crate json file created by using NII-DG library. Data governance is performed based on the RO-Crate as an input.

### POST /validate
Access the POST endpoint `/validate` with your RO-Crate as a request body to request governance.

```
$ curl -X POST localhost:5000/validate -H "Content-Type: application/json" -d @path/to/ro-crate-metadata

```
You get request_id