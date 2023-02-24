#!/usr/bin/env python3
# coding: utf-8
import datetime
from typing import Any, List, Literal, Union

import pytest

from nii_dg.entity import RootDataEntity
from nii_dg.error import PropsError
from nii_dg.schema.amed import File as AmedFile
from nii_dg.schema.base import File as BaseFile
from nii_dg.schema.base import Organization, Person
from nii_dg.utils import (EntityDef, IdDict, access_url, check_all_prop_types,
                          check_content_formats, check_content_size,
                          check_email, check_erad_researcher_number,
                          check_isodate, check_mime_type, check_orcid_id,
                          check_phonenumber, check_prop_type,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, classify_uri,
                          convert_string_type_to_python_type,
                          extract_entity_type_list_from_string_type,
                          get_name_from_ror, import_entity_class,
                          load_entity_def_from_schema_file, split_type_str,
                          sum_file_size, verify_idlink_is_correct_type,
                          verify_is_past_date)


def test_load_entity_def_from_schema_file() -> None:
    excepted_entity_def = load_entity_def_from_schema_file("base", "Person")
    assert excepted_entity_def["@id"] == {"expected_type": "str", "required": True}
    assert excepted_entity_def["name"] == {"expected_type": "str", "required": True}
    assert excepted_entity_def["alias"] == {"expected_type": "str", "required": False}
    assert excepted_entity_def["affiliation"] == {"expected_type": "Organization", "required": True}
    assert excepted_entity_def["email"] == {"expected_type": "str", "required": True}
    assert excepted_entity_def["telephone"] == {"expected_type": "str", "required": False}

    # error
    with pytest.raises(PropsError):
        load_entity_def_from_schema_file("base", "FooBar")
    with pytest.raises(PropsError):
        load_entity_def_from_schema_file("foobar", "Person")


def test_import_entity_class() -> None:
    assert import_entity_class("base", "File") is BaseFile

    # error
    with pytest.raises(PropsError):
        import_entity_class("base", "FooBar")
    with pytest.raises(PropsError):
        import_entity_class("foobar", "File")


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
    assert convert_string_type_to_python_type("RootDataEntity") is Union[RootDataEntity, IdDict]
    assert convert_string_type_to_python_type("File", "base") is Union[BaseFile, IdDict]
    assert convert_string_type_to_python_type("List[File]", "base") is List[Union[BaseFile, IdDict]]
    assert convert_string_type_to_python_type("File", "amed") is Union[AmedFile, IdDict]

    # error
    with pytest.raises(PropsError):
        convert_string_type_to_python_type("FooBar", "base")
    with pytest.raises(PropsError):
        convert_string_type_to_python_type("DMPMetadata", "foobar")


def test_check_prop_type() -> None:
    ent = BaseFile("text.txt")

    # no error occurs with correct format
    check_prop_type(ent, "@id", "test.txt", "str")

    # error
    with pytest.raises(PropsError):
        check_prop_type(ent, "@id", "test.txt", "int")


def test_check_all_prop_types() -> None:
    ent = BaseFile("text.txt", {"test_prop": 1})
    entity_def: EntityDef = {  # type:ignore
        "test_prop": {
            "expected_type": "str",
            "required": False
        }
    }

    # error
    with pytest.raises(PropsError):
        check_all_prop_types(ent, entity_def)


def test_check_unexpected_props() -> None:
    ent = BaseFile("text.txt", {"undefined_prop": "test"})
    entity_def: EntityDef = {  # type:ignore
        "@id": {
            "expected_type": "str",
            "required": True
        }
    }

    # error
    with pytest.raises(PropsError):
        check_unexpected_props(ent, entity_def)


def test_check_required_props() -> None:
    ent = BaseFile("test")
    entity_def: EntityDef = {  # type:ignore
        "test_prop": {
            "expected_type": "str",
            "required": True
        }
    }

    with pytest.raises(PropsError):
        check_required_props(ent, entity_def)

    # no error occurred with correct format
    ent["test_prop"] = "sample_value"
    check_required_props(ent, entity_def)


def test_check_content_formats() -> None:
    file = BaseFile("https://example.com/file")

    # no error occurred with correct format
    check_content_formats(file, {
        "contentSize": check_content_size,
        "url": check_url,
        "sha256": check_sha256,
        "encodingFormat": check_mime_type,
        "sdDatePublished": check_isodate
    })

    file["contentSize"] = "15kb"
    with pytest.raises(PropsError):
        check_content_formats(file, {"contentSize": check_content_size})


def test_classify_uri() -> None:
    assert classify_uri("https://example.com") == "URL"
    assert classify_uri("file:///document/test") == "abs_path"
    assert classify_uri("/document/test") == "abs_path"
    assert classify_uri("document/test") == "rel_path"


def test_check_url() -> None:
    # no error occurred with correct format
    check_url("https://example.com")

    with pytest.raises(ValueError):
        check_url("file:///documents/file")


def test_content_size() -> None:
    # no error is occurred with correct format
    check_content_size("156B")
    check_content_size("156KB")
    check_content_size("156MB")
    check_content_size("156GB")
    check_content_size("156TB")

    with pytest.raises(ValueError):
        check_content_size("150")


def test_check_mime_type() -> None:
    # no error is occurred with correct format
    check_mime_type("text/plain")

    with pytest.raises(ValueError):
        check_mime_type("text/unknown")


def test_check_sha256() -> None:
    # no error is occurred with correct format
    check_sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    with pytest.raises(ValueError):
        check_sha256("123929084207jiljgau09u0808")


def test_check_isodate() -> None:
    # no error is occurred with correct format
    check_isodate("2023-01-01")


@pytest.mark.parametrize("wrong_date",
                         ["20230131", "2023Jan31", "2023-31-01", "2023/01/31", "2023131", "2023-02-31"])
def test_check_isodate_error(wrong_date: str) -> None:
    # error
    with pytest.raises(ValueError):
        check_isodate(wrong_date)


@pytest.mark.parametrize("correct_email",
                         ["test@example.com", "test1234@example.co.jp"])
def test_check_email(correct_email: str) -> None:
    # no error is occurred with correct format
    check_email(correct_email)


@pytest.mark.parametrize("wrong_email",
                         ["test@", "@example.co.jp", "testatexample.co.jp", ".test@example.com", "test.@example.com", "sample..test@example.com"])
def test_check_email_error(wrong_email: str) -> None:
    with pytest.raises(ValueError):
        check_email(wrong_email)


@pytest.mark.parametrize("correct_phone_number",
                         ["01-2345-6789", "0123456789", "090-1234-5678", "09012345678"])
def test_check_phone_number(correct_phone_number: str) -> None:
    # no error is occurred with correct format
    check_phonenumber(correct_phone_number)


@pytest.mark.parametrize("wrong_phone_number",
                         ["123-456", "090-12-345678", "01-2345-678a"])
def test_check_phone_number_error(wrong_phone_number: str) -> None:
    with pytest.raises(ValueError):
        check_phonenumber(wrong_phone_number)


@pytest.mark.parametrize("correct_researcher_number",
                         ["01234567", "00123456"])
def test_check_erad_researcher_number(correct_researcher_number: str) -> None:
    # no error is occurred with correct format
    check_erad_researcher_number(correct_researcher_number)


@pytest.mark.parametrize("wrong_researcher_number",
                         ["0123456", "0123456a", "0123-4567"])
def test_check_erad_researcher_number_error(wrong_researcher_number: str) -> None:
    # error
    with pytest.raises(ValueError):
        check_erad_researcher_number(wrong_researcher_number)


@pytest.mark.parametrize("correct_orcid_id",
                         ["0000-0002-3849-163X", "1234-5678-9101-1128"])
def test_check_orcid_id(correct_orcid_id: str) -> None:
    # no error is occurred with correct format
    check_orcid_id(correct_orcid_id)


@pytest.mark.parametrize("wrong_orcid_id",
                         ["0000123456778900", "1234-5678-9101-1121", "0000-0002-3849-167X"])
def test_check_orcid_id_error(wrong_orcid_id: str) -> None:
    # error
    with pytest.raises(ValueError):
        check_orcid_id(wrong_orcid_id)


def test_access_url() -> None:
    # no error is occurred with correct format
    access_url("https://example.com/")

    # error
    with pytest.raises(ValueError):
        access_url("https://www.nii.ac.jp/not_existing")


def test_verify_is_past_date() -> None:
    ent = BaseFile("sample.txt", {"wrong_type": 1})

    assert verify_is_past_date(ent, "not_existing_prop") is None

    ent["date"] = "1900-01-01"
    assert verify_is_past_date(ent, "date")

    ent["date"] = "9999-01-01"
    assert verify_is_past_date(ent, "date") is False

    ent["date"] = str(datetime.date.today())
    assert verify_is_past_date(ent, "date")

    with pytest.raises(TypeError):
        verify_is_past_date(ent, "wrong_type")


def test_get_name_from_ror() -> None:
    assert get_name_from_ror("04ksd4g47") == ["Kokuritsu Jōhōgaku Kenkyūjo", "National Institute of Informatics"]

    # error
    with pytest.raises(ValueError):
        get_name_from_ror("000000000")


def test_sum_file_size() -> None:
    file_1 = BaseFile("1", {"contentSize": "15GB"})
    file_2 = BaseFile("2", {"contentSize": "10GB"})

    assert sum_file_size("GB", [file_1, file_2]) == 25
    assert sum_file_size("B", []) == 0


def test_split_type_str() -> None:
    assert split_type_str("str", ", ") == ["str"]
    assert split_type_str("Union[int, str]"[6:-1], ", ") == ["int", "str"]
    assert split_type_str("Union[str, List[int, float]]"[6:-1], ", ") == ["str", "List[int, float]"]


def test_extract_entity_type_list_from_string_type() -> None:
    assert extract_entity_type_list_from_string_type("List[Union[File, RootDataEntity]]", "base") == [BaseFile, RootDataEntity]


def test_verify_idlink_is_correct_type() -> None:
    person = Person("https://example.com/person")
    org = Organization("https://example.com/organization")
    file = BaseFile("test")

    assert verify_idlink_is_correct_type(person, "affiliation", [org])
    assert verify_idlink_is_correct_type(person, "affiliation", [file]) is False
