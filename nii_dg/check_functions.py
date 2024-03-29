#!/usr/bin/env python3
# coding: utf-8

import mimetypes
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from nii_dg.error import EntityError

if TYPE_CHECKING:
    from nii_dg.entity import Entity


def check_entity_values(
    entity: "Entity", check_rules: Dict[str, Callable[[Any], bool]]
) -> EntityError:
    """
    Check if the values of the given Entity object are valid.

    Args:
        entity (Entity): The Entity object whose values will be checked.
        check_rules (Dict[str, Callable[[Any], bool]]): A dictionary whose keys are the names of attributes of the Entity object and whose values are check functions that take the attribute value as argument and return a boolean indicating whether the value is valid or not.

    Returns:
        EntityError: An EntityError object that contains information about invalid attribute values of the Entity object. If all attribute values are valid, an empty EntityError object is returned.

    Raises:
        TypeError: If entity is not an instance of Entity class.
    """
    error = EntityError(entity)
    for key, check_func in check_rules.items():
        if key not in entity:
            continue
        if not check_func(entity[key]):
            error.add(key, f"The value '{entity[key]}' is invalid format.")

    return error


# === Check functions ===


def is_content_size(value: str) -> bool:
    """
    Check if the value is a valid content size format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid content size format (e.g., '1KB', '1MB', '1GB', etc), False otherwise.
    """
    return re.match(r"^\d+[KMGTP]?B$", value) is not None


def is_encoding_format(value: str) -> bool:
    """
    Check if the value is a valid encoding format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid encoding format (e.g., 'text/plain', 'application/json', etc), False otherwise.
    """
    return mimetypes.guess_extension(value) is not None


def is_sha256(value: str) -> bool:
    """
    Check if the value is a valid SHA256 format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid SHA256 format (e.g., '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'), False otherwise.
    """
    return re.match(r"^[0-9a-fA-F]{64}$", value) is not None


def is_url(value: str) -> bool:
    """
    Check if the value is a valid URL format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid URL format (e.g., 'https://example.com'), False otherwise.
    """
    return re.match(r"^https?://.+$", value) is not None


def is_relative_path(value: str) -> bool:
    """
    Check if the value is a valid relative path format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid relative path format (e.g., './data.csv', 'data.csv'), False otherwise.

    Examples:
        >>> is_relative_path("./data.csv")
        True
        >>> is_relative_path("data.csv")
        True
        >>> is_relative_path("/data.csv")
        False
        >>> is_relative_path("https://example.com/data.csv")
        False
        >>> is_relative_path("file:///data.csv")
        False
    """
    if urlparse(value).scheme:
        # Check if the value has a scheme (e.g., http://, https://, file://, etc)
        return False

    return not Path(value).is_absolute()


def is_absolute_path(value: str) -> bool:
    """
    Check if the value is a valid absolute path format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid absolute path format (e.g., '/data.csv'), False otherwise.

    Examples:
        >>> is_absolute_path("./data.csv")
        False
        >>> is_absolute_path("data.csv")
        False
        >>> is_absolute_path("/data.csv")
        True
        >>> is_absolute_path("https://example.com/data.csv")
        False
        >>> is_absolute_path("file:///data.csv")
        True
    """
    if urlparse(value).scheme:
        if value.startswith("file://"):
            return True
        return False

    return Path(value).is_absolute()


def is_iso8601(value: str) -> bool:
    """
    Check if the value is a valid ISO 8601 format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid ISO 8601 format (e.g., '2021-01-01T00:00:00Z'), False otherwise.
    """
    return re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", value) is not None


def is_email(value: str) -> bool:
    """
    Check if the value is a valid email format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid email format (e.g., 'test@example.com', 'mailto:test@example.com'), False otherwise.
    """
    return re.match(r"(mailto:)?[\w\.-]+@[\w\.-]+\.\w+$", value) is not None


def is_phone_number(value: str) -> bool:
    """
    Check if the value is a valid phone number format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid phone number format, False otherwise.

    Notes:
        True cases:
            +1 (555) 123-4567
            1-555-123-4567
            +1 555 123-4567
            555-123-4567
            (555)123-4567
            +44 20 7123 1234
            020-7123-1234
            +81-90-1234-5678
        False cases:
            +1-555-123
            555123456789
            +1-555-123-4567-890
            1.555.123.4567
            1 555.123.4567
            555.123.4567.890
    """
    return (
        re.match(
            r"^\+?\d{1,4}?[-. ]?\(?(?:\d{1,3}?\)?[-. ]?\d{1,4})(?:[-. ]?\d{1,4}){0,2}$",
            value,
        )
        is not None
    )


def is_orcid(value: str) -> bool:
    """
    Check if the value is a valid ORCID format.

    Args:
        value (str): The value to be checked.

    Returns:
        bool: True if the value is a valid ORCID format (e.g., '0000-0002-1825-0097'), False otherwise.
    """
    return re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$", value) is not None


def is_url_accessible(url: str) -> bool:
    """
    Check if a URL is accessible using HEAD request.

    Args:
        url (str): The URL to be checked.

    Returns:
        bool: True if the URL is accessible, False otherwise.
    """
    try:
        req = Request(url, method="HEAD")
        res = urlopen(req)
        return res.status < 400  # type: ignore
    except Exception:
        return False
