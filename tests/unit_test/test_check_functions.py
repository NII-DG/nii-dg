#!/usr/bin/env python3
# coding: utf-8

from nii_dg.check_functions import (is_absolute_path, is_content_size,
                                    is_email, is_encoding_format, is_iso8601,
                                    is_orcid, is_phone_number,
                                    is_relative_path, is_sha256, is_url,
                                    is_url_accessible)


def test_is_content_size() -> None:
    assert is_content_size("156B")
    assert is_content_size("156KB")
    assert is_content_size("156MB")
    assert is_content_size("156GB")
    assert is_content_size("156TB")

    assert not is_content_size("1")
    assert not is_content_size("1MBKB")


def test_is_encoding_format() -> None:
    assert is_encoding_format("text/plain")
    assert is_encoding_format("application/json")

    assert not is_encoding_format("application/unknown")


def test_is_sha256() -> None:
    assert is_sha256("1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")

    assert not is_sha256("123")
    assert not is_sha256("1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdefg")


def test_is_url() -> None:
    assert is_url("https://example.com")
    assert is_url("http://example.com")

    assert not is_url("ftp://example.com")
    assert not is_url("example.com")


def test_is_relative_path() -> None:
    assert is_relative_path("./data.csv")
    assert is_relative_path("data.csv")
    assert not is_relative_path("/data.csv")
    assert not is_relative_path("https://example.com/data.csv")
    assert not is_relative_path("file:///data.csv")


def test_is_absolute_path() -> None:
    assert not is_absolute_path("./data.csv")
    assert not is_absolute_path("data.csv")
    assert is_absolute_path("/data.csv")
    assert not is_absolute_path("https://example.com/data.csv")
    assert is_absolute_path("file:///data.csv")


def test_is_iso8601() -> None:
    assert is_iso8601("2021-01-01T00:00:00Z")

    assert not is_iso8601("2021-01-01T00:00:00")
    assert not is_iso8601("20230131")
    assert not is_iso8601("2023Jan31")
    assert not is_iso8601("2023-31-01")
    assert not is_iso8601("2023/01/31")
    assert not is_iso8601("2023131")
    assert not is_iso8601("2023-02-31")


def test_is_email() -> None:
    assert is_email("test@example.com")
    assert is_email("mailto:test@example.com")

    assert not is_email("test@")
    assert not is_email("@example.co.jp")
    assert not is_email("testatexample.co.jp")


def test_is_phone_number() -> None:
    assert is_phone_number("+1 (555) 123-4567")
    assert is_phone_number("1-555-123-4567")
    assert is_phone_number("01-2345-6789")
    assert is_phone_number("0123456789")
    assert is_phone_number("090-1234-5678")
    assert is_phone_number("09012345678")

    assert not is_phone_number("01-2345-678a")


def test_is_orcid() -> None:
    assert is_orcid("0000-0002-1825-0097")

    assert not is_orcid("0000-0002-1825-009")
    assert not is_orcid("0000-0002-1825-00978")


def test_is_url_accessible() -> None:
    assert is_url_accessible("https://www.example.com")

    assert not is_url_accessible("https://github.com/NII-DG/nii-dg/404")
