#!/usr/bin/env python3
# coding: utf-8

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from nii_dg.entity import ContextualEntity, DataEntity, DefaultEntity, Entity
from nii_dg.error import PropsError, UnexpectedImplementationError
from nii_dg.utils import (check_prop_type, check_required_key, github_branch,
                          github_repo, load_entity_expected_types)


class RootDataEntity(DefaultEntity):
    """\
    See https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity.
    """

    def __init__(self, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="./", props=props)
        self["@type"] = "Dataset"

    @property
    def context(self) -> str:
        """/
        Special context for RootDataEntity.
        """
        template = "https://raw.githubusercontent.com/{repo}/{branch}/schema/context/{schema}/{entity}.json"
        return template.format(
            repo=github_repo(),
            branch=github_branch(),
            schema=self.schema,
            entity="RootDataEntity",
        )

    @property
    def schema(self) -> str:
        return Path(__file__).stem

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        required_terms: List[str] = [
            "@id",
            "@type",
            "name",
            "funder"
        ]
        check_required_key(self, required_terms)

        type_schema = load_entity_expected_types(self.schema, self.__class__.__name__)

        for k, v in self.items():
            try:
                if k in ["@type", "@context"]:
                    continue
                check_prop_type(self, k, v, type_schema[k])
            except KeyError:
                raise PropsError(f"The term {k} is not defined as a usable property in {self}.") from None

    def validate(self) -> None:
        # TODO: impl.
        pass


class File(DataEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema(self) -> str:
        return Path(__file__).stem

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        required_terms: List[str] = [
            "@id",
            "@type",
            "name",
            "contentSize"
        ]
        check_required_key(self, required_terms)

        type_schema = load_entity_expected_types(self.schema, self.__class__.__name__)

        for k, v in self.items():
            try:
                if k in ["@type", "@context"]:
                    continue
                check_prop_type(self, k, v, type_schema[k])
            except KeyError:
                raise PropsError(f"The term {k} is not defined as a usable property in {self}.") from None

        try:
            idtype = is_url_or_path(self["@id"])
        except ValueError:
            raise TypeError("Value of '@id' MUST be URL of file path.") from None

        if idtype == "url":
            required_keys["sdDatePublished"] = str
        elif idtype == "path":
            if self["@id"].endswith('/'):
                raise ValueError("Value of '@id' in File entity MUST not end with '/'.")
            optional_keys["sdDatePublished"] = str

        for k in required_keys:
            check_required_key(self, k)

        for k, v in {**required_keys, **optional_keys}.items():
            try:
                check_type(self, k, v)
            except KeyError:
                pass

        check_content_size(self["contentSize"])

        try:
            check_mime_type(self["encodingFormat"])
            check_sha256(self["sha256"])
            if is_url_or_path(self["url"]) != "url":
                raise ValueError
            datetime.datetime.strptime(self["sdDatePublished"], "%Y-%m-%d")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        pass


class Dataset(DataEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema(self) -> str:
        return Path(__file__).stem

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        # TODO: impl.
        pass

    def validate(self) -> None:
        # TODO: impl.
        pass


class Organization(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)


class Person(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)


class License(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)


class RepositoryObject(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)


class DataDownload(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)


class HostingInstitution(Organization):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)


class ContactPoint(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)
