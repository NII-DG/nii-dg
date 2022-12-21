#!/usr/bin/env python3
# coding: utf-8

import datetime
import re
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from nii_dg.entity import ContextualEntity, DataEntity, DefaultEntity, Entity
from nii_dg.utils import github_branch, github_repo


def check_type(ent: Entity, key: str, type: Union[type, List[type]]) -> None:
    '''
    Check the type of the value is correct.
    If not correct, raise TypeError.
    '''
    if isinstance(type, list):
        for e in ent[key]:
            if not isinstance(e, type[0]):
                raise TypeError("Elements of '{key}' list MUST be {typename}.".format(
                    key=key,
                    typename=type[0].__name__
                ))
    else:
        if not isinstance(ent[key], type):
            raise TypeError("The value of '{key}' MUST be {typename}.".format(
                key=key,
                typename=type.__name__
            ))


def check_required_key(ent: Entity, key: str) -> None:
    '''
    Check required key is existing or not.
    If not, raise TypeError.
    '''
    try:
        ent[key]
    except KeyError:  # define validation error
        raise TypeError("The required term '{key}' is not found in the {entity}.".format(
            key=key,
            entity=ent.__class__.__name__
        )) from None


def is_url_or_path(value: str) -> Optional[str]:
    '''
    Check value is in format of URL or path.
    If not either, raise ValueError.
    '''
    encoded_value = urllib.parse.quote(value, safe="!#$&'()*+,/:;=?@[]\\")

    urlpattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    urlmatch = re.compile(urlpattern)

    if urlmatch.match(encoded_value):
        return "url"

    pathpattern = r"[\w/:%\.\\]+"
    pathmatch = re.compile(pathpattern)

    if pathmatch.match(encoded_value):
        return "path"

    raise ValueError


def check_content_size(value: str) -> None:
    '''
    Check file size value is in regulation format.
    If not, raise ValueError.
    '''
    pattern = "[0-9]+B"
    sizematch = re.compile(pattern)

    if sizematch.match(value):
        pass
    else:
        raise ValueError("File size MUST be integer with suffix 'B' as unit.")


def check_mime_type(value: str) -> None:
    '''
    Check encoding format value is in MIME type format.
    If not, raise ValueError.
    '''
    pattern = r"(application|multipart|video|model|message|image|example|font|audio|text)/[\w\-\.\+]+"
    sizematch = re.compile(pattern)

    if sizematch.match(value):
        pass
    else:
        raise ValueError("File size MUST be integer with suffix 'B' as unit.")


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
        '''
        Check properties based on the schema of RootDataEntity.
        - @id: Set './' at the constructor. No checl is done here.
        - name: Required. MUST be string.
        - description: Optional. MUST be string.
        - funder: Required. MUST be an array of Organization entity.
        - dateCreated: 自動生成?
        - creator: Required. Must be an array of Person entity.
        - repository: Optional. Must be RepositoryObject entity.
        - distribution: Optional. Must be DataDownload entity.
        - hasPart: Will be set at RO-Crate Class. No check is done here.
        '''
        required_keys: Dict[str, Union[type, List[type]]] = {
            "name": str,
            "funder": [Organization],
            "creator": [Person]
        }
        optional_keys: Dict[str, Union[type, List[type]]] = {
            "description": str,
            "repository": RepositoryObject,
            "distribution": DataDownload
        }

        for k in required_keys:
            check_required_key(self, k)

        for k, v in {**required_keys, **optional_keys}.items():
            try:
                check_type(self, k, v)
            except KeyError:
                pass

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
        '''
        Check properties based on the schema of File.
        - @id: Required. MUST be path to the file or URL.
        - name: Required. MUST be string.
        - contentSize: Required. MUST be an integer of the file size with the suffix `B` as a unit, bytes.
        - encodingFormat: Optional. MUST be MIME type.
        - sha256: Optional. MUST be the SHA-2 SHA256 hash of the file.
        - url: Optional. Must be URL.
        - sdDatePublished: Required when the file is from outside the RO-Crate Root. MUST be a string in ISO 8601 date format.
        '''
        required_keys: Dict[str, Union[type, List[type]]] = {
            "@id": str,
            "name": str,
            "contentSize": str,
        }
        optional_keys: Dict[str, Union[type, List[type]]] = {
            "encodingFormat": str,
            "sha256": str,
            "url": str
        }

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
