#!/usr/bin/env python3
# coding: utf-8

import sys
from pathlib import Path
from typing import Any, Dict, List, TypedDict

import yaml

Prop = TypedDict("Prop", {
    "description": str,
    "example": str,
    "expected_type": str
})
prop_keys = set(Prop.__annotations__.keys())
Entity = Dict[str, Prop]
Schema = Dict[str, Entity]


def validate_and_format(schema: Any) -> Schema:
    if not isinstance(schema, dict):
        raise Exception("Schema must be a dict")
    formatted_schema = {}
    for entity_name, entity in schema.items():
        if not isinstance(entity, dict):
            raise Exception(f"Entity: {entity_name} must be a dict")
        formatted_entity = {}
        for prop_name, prop in entity.items():
            if not isinstance(prop, dict):
                raise Exception(f"Prop: {prop_name} in entity: {entity_name} must be a dict")
            for prop_key in prop.keys():
                if prop_key not in prop_keys:
                    raise Exception(f"Invalid prop key: {prop_key} in prop: {prop_name} in entity: {entity_name}")
            formatted_prop = {}
            for expected_key in prop_keys:
                formatted_prop[expected_key] = " ".join(prop.get(expected_key, "").strip().split("\n"))
            formatted_entity[prop_name] = formatted_prop
        formatted_schema[entity_name] = formatted_entity

    return formatted_schema  # type: ignore


def main(args: List[str]) -> None:
    try:
        if len(args) != 2:
            raise Exception("Usage: validate_and_format_yml.py <schema_file> > <formatted_schema_file>")
        schema_file = Path(args[1]).resolve()
        if not schema_file.exists():
            raise Exception(f"Schema file {schema_file} does not exist")
        with schema_file.open("r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)
        formatted_schema = validate_and_format(schema)
        print(yaml.dump(
            formatted_schema,
            default_flow_style=False,
            indent=4,
        ))

    except Exception as e:
        print(e)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
