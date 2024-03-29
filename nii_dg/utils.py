#!/usr/bin/env python3
# coding: utf-8

"""
This module provides utility functions for nii_dg.
"""

import ast
import importlib
import importlib.util
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import (TYPE_CHECKING, Any, Dict, List, Literal, NewType, Optional,
                    Tuple, TypedDict, Union, get_args, get_origin)
from urllib.error import HTTPError
from urllib.request import urlopen

import yaml

from nii_dg.const import RO_CRATE_CONTEXT
from nii_dg.module_info import GH_REF, GH_REPO

if TYPE_CHECKING:
    from nii_dg.entity import Entity


HERE = Path(__file__).parent.resolve()


NOW = datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def load_config() -> Dict[str, Any]:
    DEFAULT_CONFIG = {
        "DG_HOST": "0.0.0.0",
        "DG_PORT": 5000,
        "DG_USE_EXTERNAL_CTX": False,
        "DG_ALLOW_OTHER_GH_REPO": False,
        "DG_WSGI_SERVER": "waitress",
        "DG_WSGI_THREADS": 1,
    }

    def str2bool(val: Union[str, bool]) -> bool:
        if isinstance(val, bool):
            return val
        if val.lower() in ("yes", "true", "t", "y", "1"):
            return True
        if val.lower() in ("no", "false", "f", "n", "0"):
            return False
        return bool(val)

    config = DEFAULT_CONFIG.copy()
    for key in DEFAULT_CONFIG.keys():
        if key in os.environ:
            if key in ("DG_USE_EXTERNAL_CTX", "DG_ALLOW_OTHER_GH_REPO"):
                config[key] = str2bool(os.environ[key])
            elif key in ("DG_PORT", "DG_WSGI_THREADS"):
                config[key] = int(os.environ[key])
            else:
                config[key] = os.environ[key]

    return config


DG_CONFIG = load_config()


def generate_ctx(
    gh_repo: str = GH_REPO, gh_ref: str = GH_REF, schema_name: str = "ro-crate"
) -> str:
    """
        Generate a context string for a given schema name.

    Args:
        gh_repo (str, optional): The name of the GitHub repository. Defaults to GH_REPO.
        gh_ref (str, optional): The name of the GitHub reference. Defaults to GH_REF.
        schema_name (str, optional): The name of the schema. Defaults to "ro-crate".

    Returns:
        str: The context string.
    """
    if schema_name == "ro-crate":
        # Called from DefaultEntities; returns RO-Crate Context
        return RO_CRATE_CONTEXT  # type: ignore

    template = "https://raw.githubusercontent.com/{gh_repo}/{gh_ref}/schema/context/{schema}.jsonld"
    return template.format(
        gh_repo=gh_repo,
        gh_ref=gh_ref,
        schema=schema_name,
    )


def parse_ctx(ctx: str) -> Tuple[str, str, str]:
    """
    Parse the given context string and return a tuple of (gh_repo, gh_ref, schema_name).

    Args:
        ctx (str): The context string to be parsed.

    Returns:
        Tuple[str, str, str]: A tuple of (gh_repo, gh_ref, schema_name).

    Raises:
        ValueError: If the given context string does not match the expected format, e.g., https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/base.jsonld
    """
    if ctx == RO_CRATE_CONTEXT:
        return GH_REPO, GH_REF, "ro-crate"

    pattern = r"https://raw\.githubusercontent\.com/(?P<gh_repo>[^/]+/[^/]+)/(?P<gh_ref>[^/]+)/schema/context/(?P<schema>[^/]+)\.jsonld"
    match = re.match(pattern, ctx)

    if match:
        gh_repo = match.group("gh_repo")
        gh_ref = match.group("gh_ref")
        schema_name = match.group("schema")
        return (gh_repo, gh_ref, schema_name)

    raise ValueError(
        "Context does not match the expected format, e.g., https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/base.jsonld"
    )


# === Definition for schema file ===

PropDef = TypedDict(
    "PropDef",
    {
        "expected_type": str,
        "example": Optional[str],
        "required": str,
        "description": str,
    },
)
# {"prop_name": PropDef}
PropsDef = NewType("PropsDef", Dict[str, PropDef])
EntityDef = TypedDict("EntityDef", {"description": str, "props": PropsDef})
# {"entity_name": EntityDef}
SchemaDef = NewType("SchemaDef", Dict[str, EntityDef])

# ==================================


def load_schema_file(schema_path: Path) -> SchemaDef:
    """
    Load a schema file and return a SchemaDef object.

    Args:
        schema_path (Path): The path to the schema file.

    Returns:
        SchemaDef: The schema definition.

    Raises:
        FileNotFoundError: If the schema file is not found.
    """
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    with schema_path.open(mode="r", encoding="utf-8") as f:
        return yaml.safe_load(f)  # type: ignore


def import_custom_class(module_name: str, class_name: str) -> Any:
    """
    Import a custom class from a module.

    Args:
    module_name (str): The name of the module containing the class.
    class_name (str): The name of the class to be imported.

    Returns:
        Any: The imported class if found, None otherwise.
    """
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except (ModuleNotFoundError, AttributeError):
        return None


def download_schema(
    gh_repo: str, gh_ref: str, schema_module_name: str
) -> Tuple[Path, Path]:
    """
    Download a schema module from a GitHub repository.

    Args:
        gh_repo (str): The GitHub repository from which the schema module is to be downloaded.
        gh_ref (str): The reference (branch, tag, or commit) of the GitHub repository.
        schema_module_name (str): The name of the schema module to be downloaded.

    Returns:
        Tuple of paths to the downloaded Python and YAML files.

    Note:
        Downloaded schema modules are stored in a temporary directory.
    """
    schema_module_url = f"https://raw.githubusercontent.com/{gh_repo}/{gh_ref}/nii_dg/schema/{schema_module_name}.py"
    schema_file_url = f"https://raw.githubusercontent.com/{gh_repo}/{gh_ref}/nii_dg/schema/{schema_module_name}.yml"

    schema_dir = tempfile.mkdtemp(prefix="nii_dg_")

    try:
        schema_module_path = Path(schema_dir).joinpath(f"{schema_module_name}.py")
        with urlopen(schema_module_url) as res:
            schema_module = res.read().decode("utf-8")
        with schema_module_path.open("w") as f:
            f.write(schema_module)
        schema_file_path = Path(schema_dir).joinpath(f"{schema_module_name}.yml")
        with urlopen(schema_file_url) as res:
            schema_file = res.read().decode("utf-8")
        with schema_file_path.open("w") as f:
            f.write(schema_file)
    except HTTPError as e:
        if e.code == 404:
            raise ValueError(
                f"Schema module '{schema_module_name}' does not exist in the given GitHub repository."
            )
        else:
            raise e

    return schema_module_path, schema_file_path


# Cache for imported external modules
_module_cache: Dict[str, Any] = {}


def import_external_class(
    gh_repo: str, gh_ref: str, schema_module_name: str, class_name: str
) -> Any:
    """
    Import a class from an external module.

    Args:
        gh_repo (str): The GitHub repository from which the schema module is to be downloaded.
        gh_ref (str): The reference (branch, tag, or commit) of the GitHub repository.
        schema_module_name (str): The name of the schema module to be downloaded.
        class_name (str): The name of the class to be imported.

    Returns:
        Any: The imported class if found, None otherwise.
    """
    module_key = f"{gh_repo}/{gh_ref}/{schema_module_name}"

    try:
        # Check if the module has already been imported
        if module_key in _module_cache:
            external_module = _module_cache[module_key]
            return getattr(external_module, class_name)

        # Download the schema module
        schema_module_path, _ = download_schema(gh_repo, gh_ref, schema_module_name)

        spec = importlib.util.spec_from_file_location(
            "external_module", schema_module_path
        )
        external_module = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(external_module)  # type: ignore

        # Cache the imported module
        _module_cache[module_key] = external_module

        return getattr(external_module, class_name)
    except (ModuleNotFoundError, AttributeError):
        return None


def is_instance_of_expected_type(value: Any, expected_type: str) -> bool:
    """
    Check if a given value is an instance of a given expected type.

    Args:
        value (Any): The value to be checked.
        expected_type (str): The expected type.

    Returns:
        bool: True if the given value is an instance of the given expected type, False otherwise.
    """

    def parse_type_string(type_str: str) -> Any:
        """
        Parse a type string and return the corresponding type object.

        Args:
            type_str (str): The type string to be parsed.

        Returns:
            Any: The type object corresponding to the given type string. e.g., "List[int]" -> typing.List[int]

        Notes:
            ast.parse returns a ast.Module object as follows:

            "List[int]" ->
                Subscript(value=Name(id='List', ctx=Load()), slice=Index(value=Name(id='int', ctx=Load())), ctx=Load())
            "Dict[str, int]" ->
                Subscript(value=Name(id='Dict', ctx=Load()), slice=Index(value=Tuple(
                    elts=[Name(id='str', ctx=Load()), Name(id='int', ctx=Load())], ctx=Load())), ctx=Load())
            "str" -> Name(id='str', ctx=Load())
            "List" -> Name(id='List', ctx=Load())
            "Entity" -> Name(id='Entity', ctx=Load())

            ---

            Optional[str] -> Union[str, NoneType]
        """
        type_node = ast.parse(type_str).body[0].value  # type: ignore
        return ast_to_type(type_node)

    def ast_to_type(node: ast.AST) -> Any:
        """
        Convert an AST node to a type object.

        Args:
            node (ast.AST): The AST node to be converted.

        Returns:
            Any: The type object corresponding to the given AST node.
        """
        if isinstance(node, ast.Name):
            if node.id in ("List", "Dict", "Tuple", "Union", "Optional", "Literal"):
                return getattr(importlib.import_module("typing"), node.id)
            elif node.id in ("str", "int", "float", "bool"):
                return eval(node.id)
            else:
                custom_class = import_custom_class("nii_dg.entity", node.id)
                if custom_class is None:
                    return Any
                return custom_class
        elif isinstance(node, ast.Subscript):
            origin = ast_to_type(node.value)  # e.g., typing.List
            args = []
            if isinstance(node.slice, ast.Index):  # use for python3.8
                slice_value = node.slice.value  # type: ignore
            else:  # use for python3.9 and later
                slice_value = node.slice  # type: ignore
            if isinstance(slice_value, ast.Tuple):
                args = [ast_to_type(arg) for arg in slice_value.elts]
            else:
                args.append(ast_to_type(slice_value))

            return origin[tuple(args) if len(args) > 1 else args[0]]
        elif isinstance(node, ast.Constant):
            # for Literal
            return node.value
        else:
            return Any

    def check_type(value: Any, expected_type: Any) -> bool:
        """
        Check if a given value is an instance of a given expected type.

        Args:
            value (Any): The value to be checked.
            expected_type (Any): The expected type.

        Returns:
            bool: True if the given value is an instance of the given expected type, False otherwise.
        """
        origin = get_origin(expected_type)  # typing.List -> list
        args = get_args(expected_type)  # typing.List[int] -> (int,)

        if origin is Union:
            # including Optional
            return any(check_type(value, t) for t in args)
        elif origin is dict:
            if not isinstance(value, dict):
                return False
            key_type, value_type = args
            return all(
                check_type(k, key_type) and check_type(v, value_type)
                for k, v in value.items()
            )
        elif origin is list:
            if not isinstance(value, list):
                return False
            item_type = args[0]
            return all(check_type(item, item_type) for item in value)
        elif origin is tuple:
            if not isinstance(value, tuple):
                return False
            item_types = args
            if len(item_types) != len(value):
                return False
            return all(
                check_type(item, item_type)
                for item, item_type in zip(value, item_types)
            )
        elif origin is Literal:
            return value in args
        elif expected_type is Any:
            return True
        elif expected_type in (str, int, float, bool):
            return isinstance(value, expected_type)
        else:
            # custom class, e.g., Entity
            if isinstance(value, dict):
                # Skip check for custom classes if value is a dictionary, e.g., {"@id": "foo", "@type": "Entity"}
                return True

            # Check if value is an instance of expected_type or its subclasses
            for cls in value.__class__.__mro__:
                if cls.__name__ == expected_type.__name__:
                    return True

            return isinstance(value, expected_type)

    parsed_expected_type = parse_type_string(expected_type)
    # parsed_expected_type: e.g., typing.List[int], typing.Dict[str, int], int, etc.

    return check_type(value, parsed_expected_type)


def is_semantic_version(version: str) -> bool:
    """
    Check if a given string is a semantic version.

    Args:
        version (str): The string to be checked.

    Returns:
        bool: True if the given string is a semantic version, False otherwise.
    """
    return re.fullmatch(r"\d+\.\d+\.\d+", version) is not None


def is_version_newer(ver1: str, ver2: str) -> bool:
    """
    Compare two version strings in semantic versioning format.

    Args:
        ver1 (str): The first version.
        ver2 (str): The second version.

    Returns:
        bool: True if the first version is newer than the second version, False otherwise.
    """
    ver1_split = ver1.split(".")
    ver2_split = ver2.split(".")

    while len(ver1_split) < len(ver2_split):
        ver1_split.append("0")
    while len(ver2_split) < len(ver1_split):
        ver2_split.append("0")

    for i in range(len(ver1_split)):
        if int(ver1_split[i]) > int(ver2_split[i]):
            return True
        elif int(ver1_split[i]) < int(ver2_split[i]):
            return False

    return False


def sum_file_size(size_unit: str, entities: List["Entity"]) -> float:
    """
    Sum the file sizes of the given entities and convert the result to the specified unit.

    Args:
        size_unit (str): The unit of the file size to be summed. e.g., "B", "KB", "MB", "GB", "TB", "PB"
        entities (List[Entity]): The entities whose file sizes are to be summed.

    Returns:
        float: The sum of the file sizes of the given entities in the specified unit.
    """
    unit_conversion_table = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "PB": 1024**5,
    }
    if size_unit not in unit_conversion_table:
        raise ValueError(f"Invalid size unit: {size_unit}")

    total_size = 0
    for entity in entities:
        if "contentSize" not in entity:
            raise ValueError(f"contentSize is not defined for {entity}")
        match = re.match(r"^(?P<size>\d+)(?P<unit>[KMGTP]?B)$", entity["contentSize"])
        if match is None:
            raise ValueError(f"Invalid content size: {entity['contentSize']}")
        size = int(match.group("size"))
        unit = match.group("unit")
        total_size += size * unit_conversion_table[unit]

    # round to 2 decimal places
    return round(total_size / unit_conversion_table[size_unit], 3)
