#!/usr/bin/env python3
# coding: utf-8
from typing import Any, List, Literal, Union

import pytest  # noqa: F401

from nii_dg.error import PropsError
from nii_dg.schema.base import HostingInstitution


def test_init() -> None:
    ent = HostingInstitution("https://example.com/HostingInstitution")
    assert ent["@id"] == "test"
    assert ent["@type"] == "HostingInstitution"


def test_check_props() -> None:
    ent = HostingInstitution("https://example.com/HostingInstitution")
    pass

    # error
    # with pytest.raises(PropsError) as e1:
    #     ent.check_props()
    # assert str(e1.value) == "The term name is required in <Dataset ./>."


def test_validate() -> None:
    pass
