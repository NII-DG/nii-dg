#!/usr/bin/env python3
# coding: utf-8

from nii_dg.entity import RootDataEntity
from nii_dg.utils import is_instance_of_expected_type


def test_is_instance_of_expected_type() -> None:
    # Positive test cases
    assert is_instance_of_expected_type(True, "bool")
    assert is_instance_of_expected_type(1, "int")
    assert is_instance_of_expected_type(1.0, "float")
    assert is_instance_of_expected_type("hello", "str")
    assert is_instance_of_expected_type([1, 2, 3], "List[int]")
    assert is_instance_of_expected_type({"a": 1, "b": 2}, "Dict[str, int]")
    assert is_instance_of_expected_type((1, "a"), "Tuple[int, str]")
    assert is_instance_of_expected_type(None, "Optional[str]")
    assert is_instance_of_expected_type("hello", "Union[int, str]")
    assert is_instance_of_expected_type(1, "Union[int, str]")
    assert is_instance_of_expected_type(1, "Any")
    assert is_instance_of_expected_type("foo", "Literal['foo', 'bar']")
    assert is_instance_of_expected_type([1, "a"], "List[Union[int, str]]")
    assert is_instance_of_expected_type(
        {"a": [1, 2], "b": [3, 4]}, "Dict[str, List[int]]"
    )

    assert is_instance_of_expected_type(RootDataEntity(), "RootDataEntity")

    # Negative test cases
    assert not is_instance_of_expected_type(1, "float")
    assert not is_instance_of_expected_type(1.0, "int")
    assert not is_instance_of_expected_type("hello", "int")
    assert not is_instance_of_expected_type([1, 2, 3], "List[str]")
    assert not is_instance_of_expected_type({"a": 1, "b": 2}, "Dict[str, str]")
    assert not is_instance_of_expected_type((1, "a"), "Tuple[str, int]")
    assert not is_instance_of_expected_type(None, "str")
    assert not is_instance_of_expected_type("hello", "int")
    assert not is_instance_of_expected_type(1, "str")
    assert not is_instance_of_expected_type(1, "Literal['foo', 'bar']")
    assert not is_instance_of_expected_type("foo", "Literal['bar']")
    assert not is_instance_of_expected_type([1, "a"], "List[Union[int, float]]")
    assert not is_instance_of_expected_type(
        {"a": [1, 2], "b": [3, 4]}, "Dict[str, List[str]]"
    )

    assert not is_instance_of_expected_type(RootDataEntity(), "str")
