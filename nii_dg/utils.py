#!/usr/bin/env python3
# coding: utf-8

import datetime
import importlib
import mimetypes
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import (Any, Callable, Dict, List, Literal, NewType, Optional,
                    TypedDict, Union)
from urllib.parse import quote, urlparse

import requests
import yaml
from typeguard import check_type as ori_check_type

from nii_dg.entity import Entity
from nii_dg.error import PropsError, UnexpectedImplementationError


class EntityDefDict(TypedDict):
    expected_type: str
    required: bool


IdDict = TypedDict("IdDict", {"@id": str})

EntityDef = NewType("EntityDef", Dict[str, EntityDefDict])


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


def convert_string_type_to_python_type(type_str: str, schema_name: Optional[str] = None) -> Any:
    """\
    Convert string type to python type.
    When it is subclass of Entity, id dict format {"@id":"id"} is also allowed.
    e.g. "List[Union[str, int]]" -> List[Union[str, int]]
    e.g. "Optional[Entity]" -> Optional[Union[Entity, IdDict]]
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
        child_types = tuple([convert_string_type_to_python_type(t, schema_name) for t in split_type_str(type_str[6:-1], ", ")])
        return Union[child_types]  # type: ignore
    elif type_str.startswith("Optional["):
        return Optional[convert_string_type_to_python_type(type_str[9:-1], schema_name)]
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
                if type_str == "ROCrateMetadata" or type_str == "RootDataEntity":
                    module = importlib.import_module("nii_dg.entity")
                    return Union[getattr(module, type_str), IdDict]
                raise PropsError(f"Unexpected type: {type_str}")
            else:
                return Union[entity_class, IdDict]


def check_prop_type(entity: "Entity", prop: str, value: Any, expected_type: str) -> None:
    """
    Check the type of each property by referring schema.yml.
    """
    expected_python_type = convert_string_type_to_python_type(expected_type, entity.schema_name)
    try:
        ori_check_type(prop, value, expected_python_type)
    except TypeError as e:
        ori_msg = str(e)
        type_msg = ori_msg[ori_msg.find("must be") + 8:]
        raise PropsError(f"The type of this property MUST be {type_msg}.") from None
    except Exception as e:
        raise UnexpectedImplementationError(e) from None


def check_all_prop_types(entity: "Entity", entity_def: EntityDef) -> None:
    """
    Check the type of all property in the entity by referring schema.yml.
    Called after check_unexpected_props().
    """
    error_dict = {}
    for prop, prop_def in entity_def.items():
        if prop in entity:
            try:
                check_prop_type(entity, prop, entity[prop], prop_def["expected_type"])
            except PropsError as e:
                error_dict[prop] = str(e)
    if len(error_dict) > 0:
        raise PropsError(error_dict)


def check_unexpected_props(entity: "Entity", entity_def: EntityDef) -> None:
    error_dict = {}
    for actual_prop in entity.keys():
        if actual_prop not in entity_def:
            if type(actual_prop) is str and actual_prop.startswith("@"):
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
    # TODO 名前もイケてない
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
    if type(value) is not str:
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
    if type(value) is not str:
        raise TypeError

    if mimetypes.guess_extension(value) is None:
        raise ValueError


def check_sha256(value: str) -> None:
    """
    Check sha256 value is in SHA256 format.
    """
    if type(value) is not str:
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


def access_url(url: str) -> None:
    """
    Check the url is accessible.
    """
    try:
        res = requests.get(url, timeout=(10.0, 30.0))
        res.raise_for_status()
    except requests.HTTPError as httperr:
        msg = str(httperr)
        raise ValueError(f"URL is not accessible. {msg}") from None
    except Exception as err:
        raise UnexpectedImplementationError from err


def get_name_from_ror(ror_id: str) -> List[str]:
    """
    Get organization name from ror.
    """
    api_url = "https://api.ror.org/organizations/" + ror_id

    try:
        res = requests.get(api_url, timeout=(10.0, 30.0))
        res.raise_for_status()
    except requests.HTTPError as httperr:
        if res.status_code == 404:
            raise ValueError(f"ROR ID {ror_id} does not exist.") from None
        raise UnexpectedImplementationError from httperr
    except Exception as err:
        raise UnexpectedImplementationError from err

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

    try:
        unit = units.index(size_unit)
    except ValueError as err:
        raise UnexpectedImplementationError from err

    for ent in entity_list:
        if ent["contentSize"][-2:] in units:
            file_unit = units.index(ent["contentSize"][-2:])
            file_size = int(ent["contentSize"][:-2])
        elif ent["contentSize"][-1:] in units:
            file_unit = 0
            file_size = int(ent["contentSize"][:-1])
        else:
            raise UnexpectedImplementationError

        file_size_sum += round(file_size / 1024 ** (unit - file_unit), 3)

    return file_size_sum


def split_type_str(type_str: str, delimiter: str) -> List[str]:
    """\
    Split string type with square brackets into element.
    e.g. "float, List[Union[int, str]]" -> ["float", "List[Union[int, str]]"]
    """
    split_list = type_str.split(delimiter)
    for i, t in enumerate(split_list):
        if t.count("[") > t.count("]"):
            split_list[i + 1] = t + delimiter + split_list[i + 1]
            split_list.remove(t)
        if t.count("[") < t.count("]"):
            raise PropsError(f"Unexpected type: {type_str}")
    return split_list


def extract_entity_type_list_from_string_type(type_str: str, schema_name: Optional[str] = None) -> List[Entity]:
    """\
    Extract Entity python type as a list from string type.
    e.g. "Optional[Union[EntityA, EntityB]]" -> [EntityA, EntityB]
    """
    entity_list: List[Entity] = []
    if type_str in ["bool", "str", "int", "float", "Any"] or type_str.startswith("Literal["):
        pass
    elif type_str.startswith("List["):
        entity_list.extend(extract_entity_type_list_from_string_type(type_str[5:-1], schema_name))
    elif type_str.startswith("Union["):
        child_list = split_type_str(type_str[6:-1], ", ")
        for t in child_list:
            entity_list.extend(extract_entity_type_list_from_string_type(t, schema_name))
    elif type_str.startswith("Optional["):
        entity_list.extend(extract_entity_type_list_from_string_type(type_str[9:-1], schema_name))
    else:
        if "[" in type_str:
            raise PropsError(f"Unexpected type: {type_str}")

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
            if type_str not in ["ROCrateMetadata", "RootDataEntity"]:
                raise PropsError(f"Unexpected type: {type_str}")
            module = importlib.import_module("nii_dg.entity")
            entity_list.append(getattr(module, type_str))
        else:
            entity_list.append(entity_class)

    return entity_list


def verify_idlink_is_correct_type(entity: Entity, prop: str, entity_list: List[Entity]) -> bool:
    entity_def = load_entity_def_from_schema_file(entity.schema_name, entity.entity_name)
    expected_entity_list = extract_entity_type_list_from_string_type(entity_def[prop]["expected_type"], entity.schema_name)

    for ent in entity_list:
        for ent_type in expected_entity_list:
            if isinstance(ent, ent_type):  # type:ignore
                return True
    return False
