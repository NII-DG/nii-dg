#!/usr/bin/env python3
# coding: utf-8

import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, TypedDict

import yaml

Prop = TypedDict("Prop", {
    "description": str,
    "example": str,
    "expected_type": str,
})
prop_keys = set(Prop.__annotations__.keys())
Entity = Dict[str, Prop]
Schema = Dict[str, Entity]


class ValidateError(Exception):
    pass


def validate_and_format(schema: Any) -> Schema:
    if not isinstance(schema, dict):
        raise ValidateError("Schema must be a dict")
    formatted_schema = {}
    for entity_name, entity in schema.items():
        if not isinstance(entity, dict):
            raise ValidateError(f"Entity: {entity_name} must be a dict")
        formatted_entity = {}
        for prop_name, prop in entity.items():
            if not isinstance(prop, dict):
                raise ValidateError(f"Prop: {prop_name} in entity: {entity_name} must be a dict")
            for prop_key in prop.keys():
                if prop_key not in prop_keys:
                    raise ValidateError(f"Invalid prop key: {prop_key} in prop: {prop_name} in entity: {entity_name}")
            formatted_prop = {}
            for expected_key in prop_keys:
                prop_val = prop.get(expected_key, "")
                if not isinstance(prop_val, str):
                    prop_val = str(prop_val).replace("'", '"')
                formatted_prop[expected_key] = " ".join(prop_val.strip().split("\n"))
            formatted_entity[prop_name] = formatted_prop
        formatted_schema[entity_name] = formatted_entity

    return formatted_schema  # type: ignore


def main(args: List[str]) -> None:
    try:
        if len(args) != 2:
            raise ValidateError("Usage: validate_and_format_yml.py <schema_file> > <formatted_schema_file>")
        schema_file = Path(args[1]).resolve()
        if not schema_file.exists():
            raise ValidateError(f"Schema file {schema_file} does not exist")
        with schema_file.open("r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)
        formatted_schema = validate_and_format(schema)
        print(yaml.dump(
            formatted_schema,
            width=1000,
            indent=2,
            sort_keys=False,
        ))

    except ValidateError as e:
        print(e)
        sys.exit(1)
    except Exception:
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
