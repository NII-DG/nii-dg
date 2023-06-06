#!/usr/bin/env python3
# coding: utf-8

import sys
from pathlib import Path
from typing import Dict, List, TypedDict

import yaml

Prop = TypedDict("Prop", {"description": str, "example": str, "expected_type": str})
prop_keys = set(Prop.__annotations__.keys())
Entity = Dict[str, Prop]
Schema = Dict[str, Entity]

REPO_NAME = "NII-DG/nii-dg"

TEMPLATE_DOCS = """\
# NII-DG: Schema: {schema_name}

See [GitHub - {repo} - schema/README.md](https://github.com/{repo}/blob/main/schema/README.md) for more information.\n
"""

TEMPLATE_ENTITY = """\
## {entity_name}
{description}

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
"""

TEMPLATE_PROP = """\
| `{prop_name}` | `{expected_type}` | {required} | {description} | `{example}` |
"""


def main(args: List[str]) -> None:
    try:
        if len(args) != 3:
            raise Exception("Usage: generate_docs.py <schema_file> <generated_docs>")
        schema_file = Path(args[1]).resolve()
        dst = Path(args[2]).resolve()
        if not schema_file.exists():
            raise Exception(f"Schema file {schema_file} does not exist")
        with schema_file.open("r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)
        schema_name = schema_file.stem
        docs = TEMPLATE_DOCS.format(schema_name=schema_name, repo=REPO_NAME)
        for entity_name, entity in schema.items():
            docs += TEMPLATE_ENTITY.format(
                entity_name=entity_name, description=entity["description"]
            )
            for prop_name, prop in entity["props"].items():
                docs += TEMPLATE_PROP.format(
                    prop_name=prop_name,
                    expected_type=prop["expected_type"],
                    required=prop["required"],
                    description=prop["description"],
                    example=prop["example"],
                )
            docs += "\n"

        with dst.open("w", encoding="utf-8") as f:
            f.write(docs.strip() + "\n")

    except Exception as e:
        print(e)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
