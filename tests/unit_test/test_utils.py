#!/usr/bin/env python3
# coding: utf-8
import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Union
from unittest.mock import mock_open, patch

import pytest

from nii_dg.entity import Entity, RootDataEntity
from nii_dg.error import PropsError
from nii_dg.schema.amed import File as AmedFile
from nii_dg.schema.base import File as BaseFile
from nii_dg.schema.base import Organization, Person
from nii_dg.schema.sapporo import SapporoRun
from nii_dg.utils import (EntityDef, access_url, check_all_prop_types,
                          check_content_formats, check_content_size,
                          check_email, check_erad_researcher_number,
                          check_instance_type_from_id, check_isodate,
                          check_mime_type, check_orcid_id, check_phonenumber,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, check_value_type,
                          classify_uri, convert_string_type_to_python_type,
                          download_file_from_url, generate_run_request_json,
                          get_entity_list_to_validate, get_file_sha256,
                          get_name_from_ror, get_sapporo_run_status,
                          import_entity_class,
                          load_entity_def_from_schema_file, sum_file_size,
                          verify_is_past_date)

# --- mock ---


def mocked_requests_get(*args: Any, **kwargs: Any) -> Any:
    # mock of requests.get
    class MockResponse:
        def __init__(self, json_data: Dict[str, Any], status_code: int) -> None:
            self.json_data = json_data
            self.status_code = status_code

        def json(self) -> Dict[str, Any]:
            return self.json_data

    return MockResponse({"state": "COMPLETE"}, 200)


# --- tests ---

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
    assert convert_string_type_to_python_type("bool") == (bool, 0)
    assert convert_string_type_to_python_type("str") == (str, 0)
    assert convert_string_type_to_python_type("int") == (int, 0)
    assert convert_string_type_to_python_type("float") == (float, 0)
    assert convert_string_type_to_python_type("Any") == (Any, 0)
    assert convert_string_type_to_python_type("List[str]") == (List[str], 0)
    assert convert_string_type_to_python_type("List[Any]") == (List[Any], 0)
    assert convert_string_type_to_python_type("Union[str, int]") == (Union[str, int], 0)
    assert convert_string_type_to_python_type("Union[List[str], int, bool]") == (Union[List[str], int, bool], 0)
    assert convert_string_type_to_python_type('Literal["a", "b"]') == (Literal["a", "b"], 0)

    # error: Tuple is not used in json
    with pytest.raises(PropsError):
        convert_string_type_to_python_type("Tuple[str, int]")
    # error: Too complex
    with pytest.raises(PropsError):
        convert_string_type_to_python_type("Union[List[Union[str, bool]], int]")

    # Entity subclass in schema module
    assert convert_string_type_to_python_type("RootDataEntity") == (RootDataEntity, 1)
    assert convert_string_type_to_python_type("File", "base") == (BaseFile, 1)
    assert convert_string_type_to_python_type("List[File]", "base") == (List[BaseFile], 1)
    assert convert_string_type_to_python_type("File", "amed") == (AmedFile, 1)

    # error
    with pytest.raises(PropsError):
        convert_string_type_to_python_type("FooBar", "base")
    with pytest.raises(PropsError):
        convert_string_type_to_python_type("DMPMetadata", "foobar")

    # TODO for new method

    # print(is_instance_of_expected_type([1, 2, 3], "List[int]"))  # True
    # print(is_instance_of_expected_type({"a": 1, "b": 2}, "Dict[str, int]"))  # True
    # print(is_instance_of_expected_type((1, "a"), "Tuple[int, str]"))  # True
    # print(is_instance_of_expected_type(None, "Optional[str]"))  # True
    # print(is_instance_of_expected_type("hello", "Union[int, str]"))  # True
    # print(is_instance_of_expected_type(1, "int"))  # True
    # print(is_instance_of_expected_type(1, "Any"))  # True
    # print(is_instance_of_expected_type("foo", "Literal['foo', 'bar']"))  # True
    # print(is_instance_of_expected_type([1, "a"], "List[Union[int, str]]"))  # True
    # print(is_instance_of_expected_type({"a": [1, 2], "b": [3, 4]}, "Dict[str, List[int]]"))  # True
    # print(is_instance_of_expected_type((1, "a", [1, 2, 3]), "Tuple[int, str, List[int]]"))  # True
    # print(is_instance_of_expected_type("foo", Literal["foo", "bar"]))  # True
    # print(is_instance_of_expected_type(RootDataEntity(), "RootDataEntity"))  # True
    # print(is_instance_of_expected_type({"@id": "id"}, "RootDataEntity"))  # True

    # print("=====")

    # # Negative test cases
    # print(is_instance_of_expected_type(1, "str"))  # False
    # print(is_instance_of_expected_type("baz", "Literal['foo', 'bar']"))  # False
    # print(is_instance_of_expected_type([1, 2, 3], "List[str]"))  # False
    # print(is_instance_of_expected_type({"a": 1, "b": 2}, "Dict[int, str]"))  # False
    # print(is_instance_of_expected_type((1, "a"), "Tuple[str, int]"))  # False
    # print(is_instance_of_expected_type(None, "str"))  # False
    # print(is_instance_of_expected_type("hello", "Union[float, bool]"))  # False
    # print(is_instance_of_expected_type([1, "a"], "List[int]"))  # False
    # print(is_instance_of_expected_type({"a": [1, 2], "b": [3, "a"]}, "Dict[str, List[int]]"))  # False
    # print(is_instance_of_expected_type((1, "a", [1, 2, "a"]), "Tuple[int, str, List[int]]"))  # False
    # print(is_instance_of_expected_type("foo", Literal["bar", "baz"]))  # False
    # print(is_instance_of_expected_type(RootDataEntity(), "str"))  # False


def test_check_value_type() -> None:
    # no error occurs with correct format
    check_value_type("test.txt", str)

    # error
    with pytest.raises(PropsError):
        check_value_type("test.txt", int)


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


def test_check_instance_type_from_id() -> None:
    ent_list: List[Entity] = []

    # error
    with pytest.raises(PropsError):
        check_instance_type_from_id(ent_list, Organization)
    with pytest.raises(PropsError):
        check_instance_type_from_id(ent_list, List[Organization], "list")

    # no error occurred
    org = Organization("https://example.com/org")
    ent_list.append(org)
    check_instance_type_from_id(ent_list, Organization)
    check_instance_type_from_id(ent_list, List[Organization], "list")


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


def test_get_entity_list_to_validate() -> None:
    person = Person("test", {"affiliation": "Organization A"})

    assert get_entity_list_to_validate(person) == {"affiliation": Organization}

    file = BaseFile("sample")
    assert len(get_entity_list_to_validate(file)) == 0
    assert isinstance(get_entity_list_to_validate(file), dict)


@patch("requests.get", side_effect=mocked_requests_get)
def test_get_sapporo_run_status(get_mock: Any) -> None:
    assert get_sapporo_run_status("run_id", "endpoint") == "COMPLETE"

    get_mock.assert_called_once()


@patch("builtins.open", new_callable=mock_open)
def test_download_file_from_url(open_mock: Any) -> None:
    download_file_from_url("https://example.com", Path("path/to/file"))

    open_mock.assert_called_once()


@patch("builtins.open", new_callable=mock_open, read_data=b"test")
def test_get_file_sha256(open_mock: Any) -> None:
    assert get_file_sha256(Path("path/to/file")) == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    open_mock.assert_called_once()


def test_generate_run_request_json() -> None:
    sapporo_run = SapporoRun(props={
        "sapporo_location": "https://example.com/sapporo",
        "workflow_engine_name": "CWL",
        "workflow_params": """{"fastq_1":{"location":"ERR034597_1.small.fq.gz","class":"File"},"fastq_2":{"location":"ERR034597_2.small.fq.gz","class":"File"},"nthreads":2}"""
    })
    assert generate_run_request_json(sapporo_run) == {
        "workflow_params": """{"fastq_1":{"location":"ERR034597_1.small.fq.gz","class":"File"},"fastq_2":{"location":"ERR034597_2.small.fq.gz","class":"File"},"nthreads":2}""",
        "workflow_type": None, "workflow_type_version": None, "tags": None, "workflow_engine_name": "CWL", "workflow_engine_parameters": None, "workflow_url": None, "workflow_name": None, "workflow_attachment": None}
