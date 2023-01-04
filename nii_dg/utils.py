#!/usr/bin/env python3
# coding: utf-8

import datetime
import importlib
import mimetypes
import re
from pathlib import Path
from typing import (TYPE_CHECKING, Any, Callable, Dict, List, Literal, NewType,
                    Optional, Union)
from urllib.parse import quote, urlparse

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


EntityDef = NewType("EntityDef", Dict[str, Dict[str, Union[str, bool]]])


def load_entity_def_from_schema_file(schema_name: str, entity_name: str) -> EntityDef:
    schema_file = Path(__file__).resolve().parent.joinpath(f"schema/{schema_name}.yml")
    if not schema_file.exists():
        raise PropsError(f"Tried to load {entity_name} from schema/{schema_name}.yml, but this file is not found.")
    with schema_file.open(mode="r", encoding="utf-8") as f:
        schema_obj = yaml.safe_load(f)
    if entity_name not in schema_obj:
        raise PropsError(f"Tried to load {entity_name} from schema/{schema_name}.yml, but this entity is not found.")

    entity_def: EntityDef = {}  # type: ignore
    for p_name, p_obj in schema_obj[entity_name]["props"].items():
        entity_def[p_name] = {
            "expected_type": p_obj["expected_type"],
            "required": p_obj["required"] == "Required."
        }

    return entity_def


def import_entity_class(schema_name: str, entity_name: str) -> Any:
    """\
    Import entity class from schema module.
    e.g., import_entity_class("base", "RootDataEntity") ->

    from nii_dg.schema.base import RootDataEntity
    return RootDataEntity
    """
    schema_file = Path(__file__).resolve().parent.joinpath(f"schema/{schema_name}.py")
    if not schema_file.exists():
        raise PropsError(f"Tried to import {entity_name} from schema/{schema_name}.py, but this file is not found.")
    module_name = f"nii_dg.schema.{schema_name}"
    module = importlib.import_module(module_name)
    try:
        return getattr(module, entity_name)
    except AttributeError:
        raise PropsError(f"Tried to import {entity_name} from schema/{schema_name}.py, but this entity is not found.") from None


def convert_string_type_to_python_type(type_str: str, schema_name: Optional[str] = None) -> Any:
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
        return List[convert_string_type_to_python_type(type_str[5:-1], schema_name)]  # type: ignore
    elif type_str.startswith("Union["):
        child_types = tuple([convert_string_type_to_python_type(t, schema_name) for t in type_str[6:-1].split(", ")])
        return Union[child_types]  # type: ignore
    elif type_str.startswith("Optional["):
        return Optional[convert_string_type_to_python_type(type_str[5:-1], schema_name)]
    elif type_str.startswith("Literal["):
        child_list = [t.strip('"').strip("'") for t in type_str[8:-1].split(", ")]
        return Literal[tuple(child_list)]  # type: ignore
    else:
        if "[" in type_str:
            raise PropsError(f"Unexpected type: {type_str}")
        else:
            # Entity subclass in schema module
            schema_name = schema_name or "base"
            entity_class = None
            try:
                entity_class = import_entity_class(schema_name, type_str)
            except PropsError:
                if schema_name != "base":
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


def check_all_prop_types(entity: "Entity", entity_def: EntityDef) -> None:
    """
    Check the type of property by referring schema.yml.
    Called after check_unexpected_props().
    """
    for prop, prop_def in entity_def.items():
        if prop in entity:
            check_prop_type(entity, prop, entity[prop], prop_def["expected_type"])


def check_unexpected_props(entity: "Entity", entity_def: EntityDef) -> None:
    for actual_prop in entity.keys():
        if actual_prop not in entity_def:
            if actual_prop.startswith("@"):
                continue
            raise PropsError(f"Unexpected property: {actual_prop} in {entity}")


def check_required_props(entity: "Entity", entity_def: EntityDef) -> None:
    """
    Check required prop is existing or not.
    If not, raise PropsError.
    """
    required_props = [k for k, v in entity_def.items() if v["required"]]
    for prop in required_props:
        if prop not in entity.keys():
            raise PropsError(f"The term {prop} is required in {entity}.")

# TODO 名前もイケてない


def check_content_formats(entity: "Entity", format_rules: Dict[str, Callable[str]]) -> None:
    """\
    expected as called after check_required_props(), check_all_prop_types(), check_unexpected_props()
    """
    for prop, check_method in format_rules.items():
        if prop in entity:
            try:
                check_method(entity[prop])
            except ValueError:
                raise PropsError(f"The term {prop} in {entity} is invalid format.") from None
        else:
            # Because optional field
            pass


def check_uri(entity: "Entity", key: str, is_url: Optional[Literal["url"]] = None) -> str:
    """
    Check the value is URI.
    Return 'URL' when the value starts with 'http' or 'https'
    When it is not URL, return 'abs_path' or 'rel_path.
    """
    try:
        encoded_uri = quote(entity[key], safe="!#$&'()*+,/:;=?@[]\\")
        parsed = urlparse(encoded_uri)
    except (TypeError, ValueError):
        raise PropsError(f"The term {key} in {entity} is invalid URI.") from None

    if parsed.scheme in ["http", "https"] and parsed.netloc != "":
        return "URL"
    elif is_url:
        raise PropsError(f"The term {key} in {entity} MUST be URL.")
    elif parsed.scheme != "" or encoded_uri.startswith(("/", "\\")):
        return "abs_path"
    else:
        return "rel_path"


def check_content_size(entity: "Entity", key: str) -> None:
    """
    Check file size value is in the defined format.
    """
    pattern = r"^\d+[KMGTP]?B$"
    sizematch = re.compile(pattern)

    if sizematch.fullmatch(entity[key]) is None:
        raise PropsError(f"The value of {key} in {entity} does not match the defined format. See {entity.context}")


def check_mime_type(entity: "Entity") -> None:
    """
    Check encoding format value is in MIME type format.
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


def check_isodate(entity: "Entity", key: str, past_or_future: Optional[Literal["past", "future"]] = None) -> None:
    """
    Check date is in ISO 8601 format "YYYY-MM-DD".
    """
    try:
        isodate = datetime.date.fromisoformat(entity[key])
    except ValueError:
        raise PropsError(f"The value of {key} in {entity} is not in the ISO 8601 date format.") from None

    today = datetime.date.today()
    if past_or_future == "past" and (today - isodate).days < 0:
        raise PropsError(f"The value of sdDatePublished in {entity} MUST be the date in the past.")
    if past_or_future == "future" and (today - isodate).days > 0:
        raise PropsError(f"The value of sdDatePublished in {entity} MUST be the date in the future.")


def check_email(entity: "Entity", key: str) -> None:
    """
    Check email format.
    """
    pattern = r"^[\w\-_]+(.[\w\-_]+)*@([\w][\w\-]*[\w]\.)+[A-Za-z]{2,}$"
    email_match = re.compile(pattern)

    if email_match.fullmatch(entity[key]) is None:
        raise PropsError(f"The value of {key} in {entity} is not correct email format.")


def check_phonenumber(entity: "Entity", key: str) -> None:
    """
    Check phone-number format.
    """
    pattern = r"(^0(\d{1}\-?\d{4}|\d{2}\-?\d{3}|\d{3}\-?\d{2}|\d{4}\-?\d{1})\-?\d{4}$|^0[5789]0\-?\d{4}\-?\d{4}$)"
    phone_match = re.compile(pattern)

    if phone_match.fullmatch(entity[key]) is None:
        raise PropsError(f"The value of {key} in {entity} is not correct email format.")
