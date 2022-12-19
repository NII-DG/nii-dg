#!/usr/bin/env python3
# coding: utf-8

from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity, DataEntity, DefaultEntity


class RootDataEntity(DefaultEntity):
    """\
    See https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity.
    """

    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)
        self["@type"] = "Dataset"


class File(DataEntity):
    pass


class Dataset(DataEntity):
    pass


class DMP(ContextualEntity):
    pass


class Organization(ContextualEntity):
    pass


class Person(ContextualEntity):
    pass


class License(ContextualEntity):
    pass


class HostingInstitution(ContextualEntity):
    pass


class PropertyValue(ContextualEntity):
    pass


class Erad(ContextualEntity):
    pass


class ContactPoint(ContextualEntity):
    pass
