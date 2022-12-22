#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest

from nii_dg.error import PropsError
from nii_dg.schema.amed import File as AmedFile
from nii_dg.schema.base import File as BaseFile
from nii_dg.schema.base import RootDataEntity
from nii_dg.utils import (convert_string_type_to_python_type,
                          import_entity_class, load_entity_expected_types)


def test_load_entity_expected_types() -> None:
    excepted_type = load_entity_expected_types("base", "RootDataEntity")
    assert excepted_type["@id"] == "str"

    # error
    with pytest.raises(PropsError):
        load_entity_expected_types("base", "FooBar")
        load_entity_expected_types("foobar", "RootDataEntity")


def test_import_entity_class() -> None:
    assert import_entity_class("base", "RootDataEntity") is RootDataEntity

    # error
    with pytest.raises(PropsError):
        import_entity_class("base", "FooBar")
        import_entity_class("foobar", "RootDataEntity")


def test_convert_string_type_to_python_type() -> None:
    assert convert_string_type_to_python_type("bool") is bool
    assert convert_string_type_to_python_type("str") is str
    assert convert_string_type_to_python_type("int") is int
    assert convert_string_type_to_python_type("float") is float
    assert convert_string_type_to_python_type("Any") is Any
    assert convert_string_type_to_python_type("List[str]") is List[str]
    assert convert_string_type_to_python_type("List[Any]") is List[Any]
    assert convert_string_type_to_python_type("Union[str, int]") is Union[str, int]
    assert convert_string_type_to_python_type("Union[List[str], int]") is Union[List[str], int]
    assert convert_string_type_to_python_type('Literal["a", "b"]') is Literal["a", "b"]

    # error
    with pytest.raises(PropsError):
        assert convert_string_type_to_python_type("Tuple[str, int]")

    # Entity subclass in schema module
    assert convert_string_type_to_python_type("RootDataEntity") is RootDataEntity
    assert convert_string_type_to_python_type("RootDataEntity", "base") is RootDataEntity
    assert convert_string_type_to_python_type("File", "base") is BaseFile
    assert convert_string_type_to_python_type("List[File]", "base") is List[BaseFile]
    assert convert_string_type_to_python_type("File", "amed") is AmedFile

    # error
    with pytest.raises(PropsError):
        convert_string_type_to_python_type("FooBar", "base")
        convert_string_type_to_python_type("RootDataEntity", "foobar")


def test_check_prop_type() -> None:
    # TODO impl. after impl. schema/base.py
    pass
