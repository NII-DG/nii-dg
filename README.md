# NII-DG: NII Data Governance Library

[![flake8](https://github.com/NII-DG/nii-dg/actions/workflows/flake8.yml/badge.svg?branch=main&event=push)](https://github.com/NII-DG/nii-dg/actions/workflows/flake8.yml)
[![isort](https://github.com/NII-DG/nii-dg/actions/workflows/isort.yml/badge.svg?branch=main&event=push)](https://github.com/NII-DG/nii-dg/actions/workflows/isort.yml)
[![mypy](https://github.com/NII-DG/nii-dg/actions/workflows/mypy.yml/badge.svg?branch=main&event=push)](https://github.com/NII-DG/nii-dg/actions/workflows/mypy.yml)
[![pytest](https://github.com/NII-DG/nii-dg/actions/workflows/pytest.yml/badge.svg?branch=main&event=push)](https://github.com/NII-DG/nii-dg/actions/workflows/pytest.yml)

The NII Data Governance Library (NII-DG) provides the following functionalities to achieve "Data Governance: The establishment of a system under clear organizational principles and the concrete implementation of data management."

- Definition of metadata schema and validation rules for research data management
- Packaging of research data (RO-Crate)
- Validation of research data

## Installation

Python 3.8 or higher is recommended.

```bash
# Clone this repository (main branch) or download the source code from the release page

# Install the library
$ python3 -m pip install .
```

### Docker

Execution using Docker is also possible.

```bash
$ docker run -it --rm ghcr.io/NII-DG/nii-dg:latest bash
```

## Usage

The library is divided into three main functionalities:

1. Schema definition: Definition of metadata schema and validation rules
2. Packaging: Packaging of research data (RO-Crate)
3. Validation: Data validation

![System architecture](https://github.com/NII-DG/nii-dg/assets/26019402/b062bb9e-c937-408d-98a6-ced2be909e3a)

### Usage: 1. Schema definition

Please refer to [./schema/README.md](./schema/README.md) for the schema definition.

### Usage: 2. Packaging

Packaging involves the process of packaging research data (actual data and metadata) into an RO-Crate. The input includes research data and its metadata, and the output is the generated RO-Crate file (`ro-crate-metadata.json`).

To package, use the Python library `nii_dg`.

As a minimal example:

```python
from nii_dg.ro_crate import ROCrate

crate = ROCrate()
crate.root["name"] = "Sample RO-Crate"
crate.dump("ro-crate-metadata.json")
```

The output will be:

```json
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    {
      "@id": "./",
      "@type": "Dataset",
      "@context": "https://w3id.org/ro/crate/1.1/context",
      "hasPart": [],
      "datePublished": "2023-06-08T10:47:25.390+00:00",
      "name": "Sample RO-Crate"
    },
    {
      "@id": "ro-crate-metadata.json",
      "@type": "CreativeWork",
      "@context": "https://w3id.org/ro/crate/1.1/context",
      "conformsTo": {
        "@id": "https://w3id.org/ro/crate/1.1"
      },
      "about": {
        "@id": "./"
      }
    }
  ]
}
```

For more detailed explanations, see the following items. In addition, [./tests/examples](./tests/examples) is provided as an example of use.

#### RO-Crate Metadata File Descriptor and Root Data Entity

The two entities mentioned in the minimal example above are the [required entities](https://www.researchobject.org/ro-crate/1.1/root-data-entity.html) in RO-Crate. They are as follows:

- RO-Crate Metadata File Descriptor
  - `@type`: `CreativeWork`
  - > The RO-Crate JSON-LD MUST contain a self-describing RO-Crate Metadata File Descriptor with the @id value ro-crate-metadata.json (or ro-crate-metadata.jsonld in legacy crates) and @type CreativeWork.
  - Referred to as ROCrateMetadata in this library.
  - A self-describing entity for the RO-Crate metadata file
  - Various metadata of RO-Crate itself are described
- Root Data Entity
  - `@type`: `Dataset`
  - > This descriptor MUST have an about property referencing the Root Data Entity, which SHOULD have an @id of ./.
  - Referred to as `RootDataEntity` in this library.
  - An entity that summarizes the files contained in the RO-Crate
  - Data entities (e.g., `File`, `Dataset`) are automatically added as `hasPart`

These two entities are automatically generated when creating an instance of `ROCrate`. Access to the Entity corresponding to RootDataEntity can be done using `ROCrate.root`.

#### Creating and Adding Entities to RO-Crate

Entities are created using their respective entity classes.

```python
from nii_dg.schema.base import File
from nii_dg.schema.base import Organization

file = File("https://example.com/path/to/file", props={"name": "Example file"})
organization = Organization("https://example.com/path/to/organization", props={"name": "Example organization"})

# After creation, the entities are added to the ROCrate
from nii_dg.ro_crate import ROCrate
crate = ROCrate()
crate.add(file, organization)
```

In these entity classes, the first argument passed is the `@id`. The `props` argument is used to provide metadata for the entity.

The `props` can also be set using the `__set__` method of the Python class.

```python
file["name"] = "Example file"
organization["name"] = "Example organization"

# If an entity is set, it will be set as `@id`
crate.root["funder"] = [organization]

# -> {"funder": [{"@id": "https://example.com/path/to/organization"}]}
```

The same operations can be performed on entities of schemas other than `base`.

```python
from nii_dg.schema.amed import File as AmedFile

amed_file = AmedFile("https://example.com/path/to/file", props={"name": "Example amed file"})
```

#### Handling Entities with the Same `@id`

When using multiple schemas, there is a possibility of having entities with the same `@id`. Although these entities are treated as separate nodes in JSON-LD, they are considered as separate entities with different contexts.

```python
from nii_dg.schema.amed import File as AmedFile
from nii_dg.schema.ginfork import File as GinforkFile

amed_file = AmedFile("path/to/file.txt", props={"name": "Example amed file"})
ginfork_file = GinforkFile("path/to/file.txt", props={"name": "Example ginfork file"})
```

In this case, in JSON-LD:

```json
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    ...,
    {
      "@id": "path/to/file.txt",
      "@type": "File",
      "@context": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/amed.jsonld",
      "name": "Example amed file",
    },
    {
      "@id": "path/to/file.txt",
      "@type": "File",
      "@context": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/ginfork.jsonld",
      "name": "Example ginfork file",
    }
  ]
}
```

The entities are represented as separate nodes in JSON-LD, and they have separate metadata due to different contexts.

#### Type Checking and Property Validation at the Entity Level

In this library, type checking of each property is performed during JSON-LD generation (`ROCrate.dump`). This process can also be performed at the entity level using `entity.check_props()`.

### Usage: 3. Validation

Validation is performed using `ROCrate.validate()`.

```python
import json
from nii_dg.ro_crate import ROCrate

with open("path/to/ro-crate-matadata.json") as f:
    jsonld = json.load(f)
crate = ROCrate(jsonld=jsonld)
crate.validate()
```

- This process calls the `entity.validate()` method for each entity to perform the validation.
  - Validation rules are defined in each schema file (YAML file) as natural language descriptions and implemented in `entity.validate()`.
- The validation process collects the results of each entity and displays them collectively.

Type checking (`entity.check_props()`) during packaging and validation (`entity.validate()`) are fundamentally different processes. The differences between these processes are as follows:

- `entity.check_props()`
  - Performs type checking for each property.
    - Example: Detects type mismatches, such as assigning an int to a str type.
  - Performs checks for required properties.
- `entity.validate()`
  - Performs more advanced validation.
  - Validates the "values" of each property.
  - Validates these values using relations between multiple entities.

#### Using REST API Server

For the REST API specifications, please refer to [open-api_spec.yml](./open-api_spec.yml).

For a quick start, please refer to [api-quick-start.md](./api-quick-start.md).

The environment variables for the behavior of the REST API Server are as follows:

- `DG_HOST`: Host name of the REST API Server (default: `0.0.0.0`)
- `DG_PORT`: Port number of the REST API Server (default: `5000`)
- `DG_WSGI_SERVER`: WSGI server to use (`flask` or `waitress`) (default: `flask`)
- `DG_WSGI_THREADS`: Number of threads to use for the WSGI server (default: `1`)

## External Referencing of Schemas Using JSON-LD Context

This library uses YAML schemas (e.g., [`nii_dg/schema/base.yml`](./nii_dg/schema/base.yml)) and Python modules (e.g., [`nii_dg/schema/base.py`](./nii_dg/schema/base.yml)) included in the library for research data packaging and validation. While the input for validation is the RO-Crate, there is a possibility of validating with different versions of the library where schemas and validation rules might differ. To resolve this issue, external referencing of schemas is performed using the JSON-LD `@context` property.

For example, using [`nii_dg/schema/base.yml`](./nii_dg/schema/base.yml) and [`nii_dg/schema/base.py`](./nii_dg/schema/base.yml), the generated `File` entity will be as follows:

```json
{
  "@id": "file_1.txt",
  "@type": "File",
  "@context": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/base.jsonld",
  "name": "Sample File",
  "contentSize": "128GB",
},
```

Here, the `@context` property indicates that the schema for the `File` entity is defined in [`https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/base.jsonld`](https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/base.jsonld).

```json
"File": {
  "@id": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File",
  "@context": {
    "@id": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:@id",
    "name": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:name",
    "contentSize": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:contentSize",
    "encodingFormat": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:encodingFormat",
    "sha256": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:sha256",
    "url": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:url",
    "sdDatePublished": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:sdDatePublished"
  }
}
```

This allows for external referencing of the schema and its properties for the `File` entity.

![System architecture extended](https://github.com/NII-DG/nii-dg/assets/26019402/fdbddf39-2e94-41bd-9167-1e8c1833e897)

During the actual validation process, the `@context` specified in each entity within the RO-Crate is followed to reference the YAML schema and Python module used during packaging. The library loads these files and generates entity instances. Then, using the schema and validation rules provided by the generated entity instances, the validation process is performed.

Due to security issues, these external references are off by default. By setting the following two environment variables to True, external references can be enabled.

- `DG_USE_EXTERNAL_CTX`: Enables external referencing of schemas and validation rules (default: `False`)
- `DG_ALLOW_OTHER_GH_REPO`: Enables external referencing of schemas and validation rules from other GitHub repositories (default: `False`)

---

For more information on JSON-LD Context generation, see [`./schema/REAMED.md`](./schema/REAMED.md).

The visibility of JSON-LD is an important element in this implementation. Therefore, this library uses GitHub Actions to generate and publish JSON-LD Context. The GitHub Actions for this purpose are defined in [`./.github/workflows/release.yml`](./.github/workflows/release.yml).

## Development

For development, use Docker and Docker Compose.

```bash
$ docker compose -f compose.dev.yml up -d --build
$ docker compose -f compose.dev.yml exec app bash

# in container
$ something you want to do
```

### Testing

Please refer to [./tests](./tests).

## Branch and Release

The branch management and release process are as follows:

- `main`: Latest Release
  - Direct push to `main` is prohibited
- `develop`: Development branch
- `<other>`: Branch for each feature or fix
  - Basically, development is done by branching from `develop` to `<other>` and merging to `develop`

Before creating a pull request for a new release, use the `rewrite_version.sh` script to update the version hardcoded in the library.

```bash
$ bash ./rewrite_version.sh <version>
```

Then create a pull request from `develop` to `main` and merge it.

Each release is tagged according to semantic versioning, such as `1.0.0`. And the version information is obtained in the release process by `./nii_dg/module_info.py`. Release and deployment are performed by [.github/workflows/release.yml](./.github/workflows/release.yml).

## License

[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0). See [LICENSE](https://github.com/sapporo-wes/yevis-cli/blob/main/LICENSE) for more information.
