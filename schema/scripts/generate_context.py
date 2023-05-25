#!/usr/bin/env python3
# coding: utf-8

"""
Usage:

$ python3 generate_context.py -h

Example:

# at <repo root>/schema
$ python3 scripts/generate_context.py ../nii_dg/schema/base.yml ./context/base.jsonld
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

import yaml

from nii_dg.module_info import GH_REF, GH_REPO

Prop = TypedDict("Prop", {
    "expected_type": str,
    "example": str,
    "required": str,
    "description": str,
})
Entity = TypedDict("Entity", {
    "description": str,
    "props": Dict[str, Prop],
})
Schema = Dict[str, Entity]


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate JSON-LD context file from schema file"
    )
    parser.add_argument(
        "schema_file",
        type=Path,
        help="Path to the input schema file"
    )
    parser.add_argument(
        "ctx_file_dst",
        type=Path,
        help="Destination path for generated context file. File name must be <schema_name>.jsonld (e.g., base.jsonld)"
    )

    return parser.parse_args(args)


def generate_ctx(schema: Schema, repo: str, gh_ref: str, schema_name: str) -> str:
    uri_base = f"https://raw.githubusercontent.com/{repo}/{gh_ref}"
    schema_base = f"{uri_base}/nii_dg/schema/{schema_name}.yml"

    ctx = {
        "@id": f"{uri_base}/schema/context/{schema_name}.jsonld",
        "@version": 1.1,
        "@context": {}
    }
    for entity_name, entity in schema.items():
        entity_ctx = {
            "@id": f"{schema_base}#{entity_name}",
            "@context": {}
        }
        for prop_name, _ in entity["props"].items():
            entity_ctx["@context"][prop_name] = f"{schema_base}#{entity_name}:{prop_name}"  # type: ignore
        ctx["@context"][entity_name] = entity_ctx  # type: ignore

    return json.dumps(ctx, indent=2)


def main(args: List[str]) -> None:
    try:
        parsed_args = parse_args(args[1:])
        schema_file: Path = parsed_args.schema_file.resolve()
        if not schema_file.exists():
            raise Exception(f"Schema file {schema_file} does not exist")
        with schema_file.open("r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)
        schema_name = schema_file.stem
        ctx = generate_ctx(schema, GH_REPO, GH_REF, schema_name)
        ctx_file_dst: Path = parsed_args.ctx_file_dst.resolve()
        with ctx_file_dst.open("w", encoding="utf-8") as f:
            f.write(ctx)

    except Exception as e:
        print(e)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
