#!/usr/bin/env python3
# coding: utf-8

import datetime
import importlib
import mimetypes
import re
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

import yaml
from typeguard import check_type as ori_check_type

from nii_dg.error import PropsError, UnexpectedImplementationError

if TYPE_CHECKING:
    from nii_dg.entity import Entity


def github_repo() -> str:
    # TODO use environment variable, git command, or const value (where?)
    return "ascade/nii_dg"


def github_branch() -> str:
    # TODO use environment variable, git command, or const value (where?)
    return "develop"


def load_entity_expected_types(schema: str, entity: str) -> Dict[str, str]:
    schema_file = Path(__file__).resolve().parent.joinpath(f"schema/{schema}.yml")
    if not schema_file.exists():
        raise PropsError(f"Tried to load {entity} from schema/{schema}.yml, but this file is not found.")
    with schema_file.open(mode="r", encoding="utf-8") as f:
        schema_obj = yaml.safe_load(f)
    if entity not in schema_obj:
        raise PropsError(f"Tried to load {entity} from schema/{schema}.yml, but this entity is not found.")
    return {p_name: p_obj["expected_type"] for p_name, p_obj in schema_obj[entity]["props"].items()}


def import_entity_class(schema: str, entity: str) -> Any:
    """\
    Import entity class from schema module.
    e.g., import_entity_class("base", "RootDataEntity") ->

    from nii_dg.schema.base import RootDataEntity
    return RootDataEntity
    """
    schema_file = Path(__file__).resolve().parent.joinpath(f"schema/{schema}.py")
    if not schema_file.exists():
        raise PropsError(f"Tried to import {entity} from schema/{schema}.py, but this file is not found.")
    module_name = f"nii_dg.schema.{schema}"
    module = importlib.import_module(module_name)
    try:
        return getattr(module, entity)
    except AttributeError:
        raise PropsError(f"Tried to import {entity} from schema/{schema}.py, but this entity is not found.") from None


def convert_string_type_to_python_type(type_str: str, schema: Optional[str] = None) -> Any:
    """\
    Convert string type to python type.
    e.g. "List[Union[str, int]]" -> List[Union[str, int]]
    """
    if type_str == "bool":
        return bool
    elif type_str == "str":
        return str
    elif type_str == "int":
        return int
    elif type_str == "float":
        return float
    elif type_str == "Any":
        return Any
    elif type_str.startswith("List["):
        return List[convert_string_type_to_python_type(type_str[5:-1], schema)]  # type: ignore
    elif type_str.startswith("Union["):
        child_types = tuple([convert_string_type_to_python_type(t, schema) for t in type_str[6:-1].split(", ")])
        return Union[child_types]  # type: ignore
    elif type_str.startswith("Optional["):
        return Optional[convert_string_type_to_python_type(type_str[5:-1], schema)]
    elif type_str.startswith("Literal["):
        child_list = [t.strip('"').strip("'") for t in type_str[8:-1].split(", ")]
        return Literal[tuple(child_list)]  # type: ignore
    else:
        if "[" in type_str:
            raise PropsError(f"Unexpected type: {type_str}")
        else:
            # Entity subclass in schema module
            schema = schema or "base"
            entity_class = None
            try:
                entity_class = import_entity_class(schema, type_str)
            except PropsError:
                if schema != "base":
                    try:
                        entity_class = import_entity_class("base", type_str)
                    except PropsError:
                        pass
            if entity_class is None:
                raise PropsError(f"Unexpected type: {type_str}")
            else:
                return entity_class


def check_prop_type(entity: "Entity", prop: str, value: Any, expected_type: str) -> None:
    excepted_python_type = convert_string_type_to_python_type(expected_type, entity.schema)
    try:
        ori_check_type(prop, value, excepted_python_type)
    except TypeError as e:
        ori_msg = str(e)
        base_msg = ori_msg[:ori_msg.find("must be")]
        type_msg = ori_msg[ori_msg.find("must be") + 8:]
        raise PropsError(f"The {base_msg.strip()} in {entity} MUST be {type_msg}.") from None
    except Exception as e:
        raise UnexpectedImplementationError(e)


# def check_type(ent: Entity, key: str, type: Union[type, List[type]]) -> None:
#     """
#     Check the type of the value is correct.
#     If not correct, raise TypeError.
#     """
#     if isinstance(type, list):
#         for e in ent[key]:
#             if not isinstance(e, type[0]):
#                 raise TypeError("Elements of '{key}' list MUST be {typename}.".format(
#                     key=key,
#                     typename=type[0].__name__
#                 ))
#     else:
#         if not isinstance(ent[key], type):
#             raise TypeError("The value of '{key}' MUST be {typename}.".format(
#                 key=key,
#                 typename=type.__name__
#             ))


def check_required_key(entity: "Entity", required_terms: List[str]) -> None:
    """
    Check required key is existing or not.
    If not, raise TypeError.
    """
    for k in required_terms:
        if k not in entity.keys():
            raise PropsError(f"The term {k} is required in {entity}.")


def is_url_or_path(value: str) -> Optional[str]:
    """
    Check value is in format of URL or path.
    If not either, raise ValueError.
    """
    encoded_value = urllib.parse.quote(value, safe="!#$&'()*+,/:;=?@[]\\")

    urlpattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    urlmatch = re.compile(urlpattern)

    if urlmatch.match(encoded_value):
        return "url"

    pathpattern = r"[\w/:%\.\\]+"
    pathmatch = re.compile(pathpattern)

    if pathmatch.match(encoded_value):
        return "path"

    raise ValueError


def check_content_size(entity: "Entity", key: str) -> None:
    """
    Check file size value is in the defined format.
    When it is wrong, return None.
    """
    pattern = r"^\d+[KMGTP]?B$"
    sizematch = re.compile(pattern)

    if sizematch.fullmatch(entity[key]) is None:
        raise PropsError(f"The value of {key} in {entity} does not match the defined format. See {entity.context}")


def check_mime_type(entity: "Entity") -> None:
    """
    Check encoding format value is in MIME type format.
    If not, raise ValueError.
    """
    # TODO: mimetypeの辞書がOSによって差分があるのをどう吸収するか, 例えばtext/markdown

    if mimetypes.guess_extension(entity["encodingFormat"]) is None:
        raise PropsError(f"The value of encodingFormat in {entity} does not match the MIME type.")


def check_sha256(entity: "Entity") -> None:
    """
    Check sha256 value is in SHA256 format.
    """
    pattern = r"(?:[^a-fA-F\d]|\b)([a-fA-F\d]{64})(?:[^a-fA-F\d]|\b)"
    shamatch = re.compile(pattern)

    if shamatch.fullmatch(entity["sha256"]) is None:
        raise PropsError(f"The value of sha256 in {entity} is not a hash generated by the SHA-256 algorithm.")


def check_date(entity: "Entity", key: str) -> None:
    """
    Check date is in format "YYYY-MM-DD".
    If not, raise ValueError.
    """
    try:
        datetime.datetime.strptime(entity[key], "%Y-%m-%d")
    except Exception:
        pass
