# NII-DG Schema Definition

## Components of Schema Definition

The definition of a single schema involves these files:

- YAML file (e.g., [`../nii_dg/schema/base.yml`](../nii_dg/schema/base.yml))
- Python module (e.g., [`../nii_dg/schema/base.py`](../nii_dg/schema/base.py))
- Markdown file (e.g., [`./docs/base.md`](./docs/base.md))
- JSON-LD file (e.g., [`../context/base.jsonld`](../context/base.jsonld))

The Markdown file and JSON-LD file are auto-generated from the YAML file, hence they do not need to be edited directly.

### YAML file

This file outlines the schema for each entity. For instance, in the case of the `File` entity, the schema defines three properties: `@id`, `name`, and `contentSize` as follows:

```yaml
File:
  description: A file included in the research project, such as a text file, script file, or images.
  props:
    "@id":
      expected_type: str
      example: config/setting.txt
      required: Required.
      description: MUST be either a URI Path relative to the RO-Crate root directory or an absolute URI that is directly downloadable. If the file originates outside the repository, @id SHOULD allow for simple retrieval (e.g., HTTP GET), including redirections and HTTP/HTTPS authentication. RO-Crate metadata (ro-crate-metadata.json) is excluded.
    name:
      expected_type: str
      example: setting.txt
      required: Required.
      description: Denotes the file name.
    contentSize:
      expected_type: str
      example: 1560B
      required: Required.
      description: MUST be an integer representing the file size, suffixed with `B` for bytes. Other units like "KB", "MB", "GB", "TB", and "PB" may also be used if necessary.
    ...
```

Each property is defined by:

- `expected_type`
  - The expected data type, following the Python typing module notation.
  - For example, `Dict[str, int]` is possible.
  - When referring to another entity, it is described as `List[File]`.
  - Referring to another entity is only possible within the same schema.
    - However, in the extended schema described below, it is possible to refer to entities from the common schema.
- `example`
  - An example of the property value.
- `required`
  - Indicates whether the property is required or not.
  - Possible values are `Required.` and `Optional.`.
  - For example, `Required when accessRights has Unshared or Restricted Closed Sharing.` means that the property is required under certain conditions.
    - Therefore, in the `check_props` function, the property is judged to be `Required.` if it matches exactly.
- `description`:
  - A description of the property.
  - The natural language validation rules are described in this description.

Noteworthy rules include:

- Each entity should be named in CamelCase.
- The `@id` field is required for all entities.
- The `@type` field is not required to be described in this schema definition because the name of each entity is used.
- The `@id` field is recommended to be described as a URI.

A script, [`./scripts/validate_and_format_yml.py`](./scripts/validate_and_format_yml.py), is provided for the validation and formatting of the YAML schema file as follows:

```bash
$ python3 validate_and_format_yml.py <source_yml> <dest_yml>
```

### Python Module

Each entity is defined as a Python class. For instance, the `File` entity can define its validation rules by implementing `check_props()` and `validate()` methods as follows:

```python
class File(DataEntity):
    def __init__(
        self,
        id_: str,
        props: Dict[str, Any] = {},
        schema_name: str = SCHEMA_NAME,
        entity_def: EntityDef = SCHEMA_DEF["File"],
    ):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        # Type checking process for each props called by Packaging
        pass

    def validate(self, crate: "ROCrate") -> None:
        # More advanced validation process called by Validation
        pass
```

### Markdown File

The Markdown file is a document auto-generated from the YAML schema file for easy viewing. It can be generated from the YAML schema file using [`./scripts/generate_docs.py`](./scripts/generate_docs.py) as follows:

```bash
$ python3 generate_docs.py <source_yml> <dest_md>
```

### Generate JSON-LD File

The JSON-LD file can be generated from the YAML schema file using [`./scripts/generate_jsonld.py`](./scripts/generate_jsonld.py) as follows:

```bash
$ python3 generate_jsonld.py <source_yml> <dest_jsonld>
```

## Current Schema Definitions

Schema definitions are split into two types:

- Common (base) schema
- Specific schemas for DMP, domains, and platforms (referred to as extension schemas)

The common schema includes:

- [`../nii_dg/schema/base.yml`](../nii_dg/schema/base.yml)
- [`../nii_dg/schema/base.py`](../nii_dg/schema/base.py)
- [`./docs/base.md`](./docs/base.md)
- [`../context/base.jsonld`](../context/base.jsonld)

Extension schemas have the field name as a prefix to the file name, such as [`../nii_dg/schema/amed.yml`](../nii_dg/schema/amed.yml).

The current extension schemas are:

- `cao`
  - Common metadata elements defined in the Cabinet Office's "[Basic Concepts for the Management and Utilization of Research Data Using Public Funds](https://www8.cao.go.jp/cstp/kenkyudx.html)"
  - [Reference docs](https://www8.cao.go.jp/cstp/common_metadata_elements.pdf)
- `amed`
  - Japan Agency for Medical Research and Development
  - [Reference Web Page](https://www.amed.go.jp/koubo/datamanagement.html)
- `meti`
  - Ministry of Economy, Trade and Industry
  - [Reference Web Page](https://www.meti.go.jp/policy/innovation_policy/datamanagement.html)
  - New Energy and Industrial Technology Development Organization (NEDO) and Biotechnology Research and Development Center (BRAIN) have selected this.
- `ginfork`
  - Extension schema for ginfork
- `sapporo`
  - Extension schema for Sapporo

## Schema Addition and Extension

In general, adding and extending the base schema is not anticipated as most fundamental entities, like `File` or `Person`, are defined in the common schema. Therefore, it is possible to specify the `base:Person` entity as the value for `amed:DMPMetadata:creator` in the base schema.

To define an entity in an extension schema, create YAML/Python schema files and write each correspondingly. If the entity is not defined in the base schema, write it directly. If it is defined in the base schema and you wish to change some validation rules or add some properties, inherit from the base schema's entity.
