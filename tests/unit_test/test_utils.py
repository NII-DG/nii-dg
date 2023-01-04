#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.amed import File as AmedFile
from nii_dg.schema.base import File as BaseFile
from nii_dg.schema.base import RootDataEntity
from nii_dg.utils import (EntityDef, check_content_size, check_email,
                          check_erad_researcher_number, check_isodate,
                          check_mime_type, check_phonenumber, check_prop_type,
                          check_required_props, check_sha256, check_url,
                          convert_string_type_to_python_type,
                          import_entity_class,
                          load_entity_def_from_schema_file)


def test_load_entity_def_from_schema_file() -> None:
    excepted_entity_def = load_entity_def_from_schema_file("base", "RootDataEntity")
    assert excepted_entity_def["@id"] == {"expected_type": "str", "required": True}

    # error
    with pytest.raises(PropsError):
        load_entity_def_from_schema_file("base", "FooBar")
        load_entity_def_from_schema_file("foobar", "RootDataEntity")


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
    root = RootDataEntity()

    # nothing is occurred with correct format
    check_prop_type(root, "@id", "./", "str")

    with pytest.raises(PropsError):
        check_prop_type(root, "@id", "./", "int")


def test_check_all_prop_types() -> None:
    # TODO impl. after impl. schema/base.py
    pass


def test_check_unexpected_props() -> None:
    # TODO impl. after impl. schema/base.py
    pass


def test_check_required_props() -> None:
    root = RootDataEntity()
    entity_def: EntityDef = {  # type:ignore
        "test_prop": {
            "expected_type": "str",
            "required": True
        }
    }

    with pytest.raises(PropsError):
        check_required_props(root, entity_def)

    # nothing is occurred with correct format
    root["test_prop"] = "sample_value"
    check_required_props(root, entity_def)


def test_check_content_formats() -> None:
    # TODO impl. after impl. schema/base.py
    pass


def test_classify_uri() -> None:
    # TODO impl. after impl. schema/base.py
    pass


def test_check_url() -> None:
    # nothing is occurred with correct format
    check_url("https://example.com")

    with pytest.raises(ValueError):
        check_url("file://documents/file")
    # to be added


def test_content_size() -> None:
    # nothing is occurred with correct format
    check_content_size("156B")
    check_content_size("156KB")
    check_content_size("156MB")
    check_content_size("156GB")
    check_content_size("156TB")

    with pytest.raises(ValueError):
        check_content_size("150")
    # to be added


def test_check_mime_type() -> None:
    # nothing is occurred with correct format
    check_mime_type("text/plain")

    with pytest.raises(ValueError):
        check_mime_type("text/unknown")
    # to be added


def test_check_sha256() -> None:
    # nothing is occurred with correct format
    check_sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    with pytest.raises(ValueError):
        check_sha256("123929084207jiljgau09u0808")
    # to be added


def test_check_isodate() -> None:
    # nothing is occurred with correct format
    check_isodate("2023-01-01")

    # error
    with pytest.raises(ValueError):
        check_isodate("20230101")

    with pytest.raises(ValueError):
        check_isodate("2023Jan01")

    with pytest.raises(ValueError):
        check_isodate("2023-31-01")


def test_check_email() -> None:
    # nothing is occurred with correct format
    check_email("test@example.com")
    check_email("test@example.co.jp")

    with pytest.raises(ValueError):
        check_email("abc@")


def test_check_phonenumber() -> None:
    # nothing is occurred with correct format
    check_phonenumber("01-2345-6789")
    check_phonenumber("0123456789")
    check_phonenumber("090-1234-5678")
    check_phonenumber("09012345678")

    with pytest.raises(ValueError):
        check_phonenumber("123-456")


def test_check_erad_researcher_number() -> None:
    # nothing is occurred with correct format
    check_erad_researcher_number("01234567")

    # error
    with pytest.raises(ValueError):
        check_erad_researcher_number("00123")
        check_erad_researcher_number("00123456")
