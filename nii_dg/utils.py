#!/usr/bin/env python3
# coding: utf-8

import datetime
import importlib
import mimetypes
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import (TYPE_CHECKING, Any, Callable, Dict, List, Literal, NewType,
                    Optional, Tuple, TypedDict, Union)
from urllib.parse import quote, urlparse

import requests
import yaml
from typeguard import check_type as ori_check_type

from nii_dg.error import PropsError, UnexpectedImplementationError

if TYPE_CHECKING:
    from nii_dg.entity import Entity


class EntityDefDict(TypedDict):
    expected_type: str
    required: bool


EntityDef = NewType("EntityDef", Dict[str, EntityDefDict])


def load_entity_def_from_schema_file(schema_name: Optional[str] = None, entity_name: str = "") -> EntityDef:
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
    e.g., import_entity_class("base", "File") ->

    from nii_dg.schema.base import File
    return File
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


def convert_string_type_to_python_type(type_str: str, schema_name: Optional[str] = None) -> Tuple[Any, int]:
    """\
    Convert string type to python type.
    At the same time, it determines whether entity subclasses are included in it and returns a flag.
    e.g. "List[Union[str, int]]" -> List[Union[str, int]], 0
    """
    if type_str == "bool":
        return bool, 0
    elif type_str == "str":
        return str, 0
    elif type_str == "int":
        return int, 0
    elif type_str == "float":
        return float, 0
    elif type_str == "Any":
        return Any, 0
    elif type_str.startswith("List["):
        type_, flg = convert_string_type_to_python_type(type_str[5:-1], schema_name)
        return List[type_], flg  # type: ignore
    elif type_str.startswith("Optional["):
        type_, flg = convert_string_type_to_python_type(type_str[9:-1], schema_name)
        return Optional[type_], flg
    elif type_str.startswith("Union["):
        child_types = tuple([convert_string_type_to_python_type(t, schema_name)[0] for t in type_str[6:-1].split(", ")])
        flg_list = [convert_string_type_to_python_type(t, schema_name)[1] for t in type_str[6:-1].split(", ")]
        if flg_list.count(flg_list[0]) != len(flg_list):
            raise PropsError(f"Unexpected type: {type_str}")
        return Union[child_types], flg_list[0]  # type: ignore
    elif type_str.startswith("Literal["):
        child_list = [t.strip('"').strip("'") for t in type_str[8:-1].split(", ")]
        return Literal[tuple(child_list)], 0  # type: ignore
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
                if type_str in ["ROCrateMetadata", "RootDataEntity"]:
                    module = importlib.import_module("nii_dg.entity")
                    return getattr(module, type_str), 1
                raise PropsError(f"Unexpected type: {type_str}")
            else:
                return entity_class, 1


def check_prop_type(prop: str, value: Any, expected_python_type: Any) -> None:
    """
    Check the type of each property by referring schema.yml.
    When the type includes entity subclass, the check is skipped.
    """
    # expected_python_type, flg = convert_string_type_to_python_type(expected_type, entity.schema_name)
    # if flg == 1:
    #     return
    try:
        ori_check_type(prop, value, expected_python_type)
    except TypeError as e:
        ori_msg = str(e)
        type_msg = ori_msg[ori_msg.find("must be") + 8:]
        raise PropsError(f"The type of this property MUST be {type_msg}.") from None
    except Exception as e:
        raise UnexpectedImplementationError(e) from None


def check_all_prop_types(entity: "Entity", entity_def: EntityDef, subclass_flg: int = 0) -> None:
    """
    Check the type of all property in the entity by referring schema.yml.
    When the type of property includes entity subclass, the check of the property is skipped.
    Called after check_unexpected_props().
    """
    error_dict = {}
    for prop, prop_def in entity_def.items():
        if prop in entity:
            expected_python_type, flg = convert_string_type_to_python_type(prop_def["expected_type"], entity.schema_name)
            if flg == subclass_flg:
                try:
                    check_prop_type(prop, entity[prop], expected_python_type)
                except PropsError as e:
                    error_dict[prop] = str(e)
    if len(error_dict) > 0:
        raise PropsError(error_dict)


def check_instance_type_from_id(prop: str, entity_list: List["Entity"], expected_python_type: Any, list_flg: Optional[str] = None) -> None:
    correct_type_ents = []
    for ent in entity_list:
        try:
            if list_flg == "list":
                check_prop_type(prop, [ent], expected_python_type)
            else:
                check_prop_type(prop, ent, expected_python_type)
            correct_type_ents.append(ent)
        except PropsError:
            pass
    if len(correct_type_ents) == 0:
        raise PropsError("The entity liked by @id dict in this property is invalid type.")


def check_unexpected_props(entity: "Entity", entity_def: EntityDef) -> None:
    error_dict = {}
    for actual_prop in entity.keys():
        if actual_prop not in entity_def:
            if isinstance(actual_prop, str) and actual_prop.startswith("@"):
                continue
            error_dict[actual_prop] = "Unexpected property"
    if len(error_dict) > 0:
        raise PropsError(error_dict)


def check_required_props(entity: "Entity", entity_def: EntityDef) -> None:
    """
    Check required prop is existing or not.
    If not, raise PropsError.
    """
    error_dict = {}
    required_props = [k for k, v in entity_def.items() if v["required"]]
    for prop in required_props:
        if prop not in entity.keys():
            error_dict[prop] = "This property is required, but not found."

    if len(error_dict) > 0:
        raise PropsError(error_dict)


def check_content_formats(entity: "Entity", format_rules: Dict[str, Callable[[str], None]]) -> None:
    """\
    expected as called after check_required_props(), check_all_prop_types(), check_unexpected_props()
    """
    error_dict = {}
    for prop, check_method in format_rules.items():
        if prop in entity:
            try:
                check_method(entity[prop])
            except (TypeError, ValueError):
                error_dict[prop] = "The value is invalid format."
        else:
            # Because optional field
            pass
    if len(error_dict) > 0:
        raise PropsError(error_dict)


def classify_uri(value: str) -> str:
    """
    Check the value is URI.
    Return 'URL' when the value starts with 'http' or 'https'
    When it is not URL, return 'abs_path' or 'rel_path.
    """
    try:
        encoded_uri = quote(value, safe="!#$&'()*+,/:;=?@[]\\")
        parsed = urlparse(encoded_uri)
    except (TypeError, ValueError):
        raise ValueError(f"The value {value} is invalid URI.") from None

    if parsed.scheme in ["http", "https"] and parsed.netloc != "":
        return "URL"
    if PurePosixPath(encoded_uri).is_absolute() or PureWindowsPath(encoded_uri).is_absolute() or parsed.scheme == "file":
        return "abs_path"
    return "rel_path"


def check_url(value: str) -> None:
    """
    Check the value is URL.
    If not, raise ValueError.
    """
    try:
        encoded_url = quote(value, safe="!#$&'()*+,/:;=?@[]\\")
        parsed = urlparse(encoded_url)
    except TypeError:
        raise ValueError from None

    if parsed.scheme not in ["http", "https"]:
        raise ValueError
    if parsed.netloc == "":
        raise ValueError


def check_content_size(value: str) -> None:
    """
    Check file size value is in the defined format.
    If not, raise ValueError.
    """
    if not isinstance(value, str):
        raise TypeError

    pattern = r"^\d+[KMGTP]?B$"
    size_match = re.compile(pattern)

    if size_match.fullmatch(value) is None:
        raise ValueError


def check_mime_type(value: str) -> None:
    """
    Check encoding format value is in MIME type format.
    """
    # TODO: mimetypeの辞書がOSによって差分があるのをどう吸収するか, 例えばtext/markdown
    if not isinstance(value, str):
        raise TypeError

    if mimetypes.guess_extension(value) is None:
        raise ValueError


def check_sha256(value: str) -> None:
    """
    Check sha256 value is in SHA256 format.
    """
    if not isinstance(value, str):
        raise TypeError

    pattern = r"(?:[^a-fA-F\d]|\b)([a-fA-F\d]{64})(?:[^a-fA-F\d]|\b)"
    sha_match = re.compile(pattern)

    if sha_match.fullmatch(value) is None:
        raise ValueError


def check_isodate(value: str) -> None:
    """
    Check date is in ISO 8601 format "YYYY-MM-DD".
    """
    datetime.date.fromisoformat(value)


def check_email(value: str) -> None:
    """
    Check email format.
    """
    pattern = r"^[\w\-_]+(.[\w\-_]+)*@([\w][\w\-]*[\w]\.)+[A-Za-z]{2,}$"
    email_match = re.compile(pattern)

    if email_match.fullmatch(value) is None:
        raise ValueError


def check_phonenumber(value: str) -> None:
    """
    Check phone-number format.
    """
    pattern = r"(^0(\d{1}\-?\d{4}|\d{2}\-?\d{3}|\d{3}\-?\d{2}|\d{4}\-?\d{1})\-?\d{4}$|^0[5789]0\-?\d{4}\-?\d{4}$)"
    phone_match = re.compile(pattern)

    if phone_match.fullmatch(value) is None:
        raise ValueError


def check_erad_researcher_number(value: str) -> None:
    """
    Confirm check digit
    """
    if len(value) != 8:
        raise ValueError

    check_digit = int(value[0])
    sum_val = 0
    for i, num in enumerate(value):
        if i == 0:
            continue
        if i % 2 == 0:
            sum_val += int(num) * 2
        else:
            sum_val += int(num)

    if (sum_val % 10) != check_digit:
        raise ValueError


def check_orcid_id(value: str) -> None:
    """
    Check orcid id format and checksum.
    """
    pattern = r"^(\d{4}-){3}\d{3}[\dX]$"
    orcidid_match = re.compile(pattern)

    if orcidid_match.fullmatch(value) is None:
        raise ValueError(f"Orcid ID {value} is invalid.")

    if value[-1] == "X":
        checksum = 10
    else:
        checksum = int(value[-1])
    sum_val = 0
    for num in value.replace("-", "")[:-1]:
        sum_val = (sum_val + int(num)) * 2
    if (12 - (sum_val % 11)) % 11 != checksum:
        raise ValueError(f"Orcid ID {value} is invalid.")


def verify_is_past_date(entity: "Entity", key: str) -> Optional[bool]:
    """
    Check the date is past or not.
    """
    if key not in entity.keys():
        return None

    iso_date = datetime.date.fromisoformat(entity[key])
    today = datetime.date.today()

    if (today - iso_date).days < 0:
        return False
    return True


def access_url(url: str) -> requests.Response:
    """
    Check the url is accessible.
    """
    try:
        res = requests.get(url, timeout=(10.0, 30.0))
        res.raise_for_status()
    except Exception as err:
        raise ValueError(f"Unable to access {url} due to {err}") from None

    return res


def get_name_from_ror(ror_id: str) -> List[str]:
    """
    Get organization name from ror.
    """
    api_url = "https://api.ror.org/organizations/" + ror_id
    res = access_url(api_url)

    body = res.json()
    name_list: List[str] = body["aliases"]
    name_list.append(body["name"])
    return name_list


def sum_file_size(size_unit: str, entity_list: List["Entity"]) -> float:
    """
    Sum size of file entities in the specified unit.
    """
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    file_size_sum: float = 0
    target_prop = "contentSize"

    try:
        unit = units.index(size_unit)
    except ValueError as err:
        raise UnexpectedImplementationError from err

    for ent in entity_list:
        if ent[target_prop][-2:] in units:
            file_unit = units.index(ent[target_prop][-2:])
            file_size = int(ent[target_prop][:-2])
        elif ent[target_prop][-1:] in units:
            file_unit = 0
            file_size = int(ent[target_prop][:-1])
        else:
            raise UnexpectedImplementationError

        file_size_sum += round(file_size / 1024 ** (unit - file_unit), 3)

    return file_size_sum


def get_entity_list_to_validate(entity: "Entity") -> Dict[str, Any]:
    entity_def = load_entity_def_from_schema_file(entity.schema_name, entity.entity_name)
    instance_type_dict = {}
    for prop, prop_def in entity_def.items():
        if prop in entity:
            expected_python_type, flg = convert_string_type_to_python_type(prop_def["expected_type"], entity.schema_name)
            if flg == 1:
                print("instance")
                instance_type_dict[prop] = expected_python_type

    return instance_type_dict
