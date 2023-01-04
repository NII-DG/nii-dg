#!/usr/bin/env python3
# coding: utf-8

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from nii_dg.entity import ContextualEntity, DataEntity, DefaultEntity, Entity
from nii_dg.error import (GovernanceError, PropsError,
                          UnexpectedImplementationError)
from nii_dg.utils import (check_all_prop_types, check_content_size,
                          check_email, check_isodate, check_mime_type,
                          check_phonenumber, check_required_props,
                          check_sha256, check_uri, github_branch, github_repo,
                          load_entity_def_from_schema_file)


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
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        requires = [prop for prop in schema["required_list"] if prop not in ["dateCreated", "hasPart"]]
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)
        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_required_props(self, requires)
        check_all_prop_types(self, schema["type_dict"])

    def validate(self) -> None:
        # TODO: impl.
        pass


class File(DataEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:

        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        if check_uri(self, "@id") == "abs_path":
            raise PropsError(f"The @id value in {self} MUST be URL or relative path to the file, not absolute path.")
        check_content_size(self, "contentSize")

        try:
            check_mime_type(self)
            check_sha256(self)
            check_uri(self, "url", "url")
            check_isodate(self, "sdDatePublished", "past")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        # @idがURLの場合にsdDatePublishedの存在チェック
        if check_uri(self, "@id") == "url":
            if "sdDatePublished" not in self.keys():
                raise GovernanceError(f"The term sdDatePublished MUST be included in {self}.")


class Dataset(DataEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        if not self["@id"].endswith("/"):
            raise PropsError(f"The @id value in {self} MUST end with '/'.")
        if check_uri(self, "@id") != "rel_path":
            raise PropsError(f"The @id value in {self} MUST be relative path to the directory, neither absolute path nor URL.")

        try:
            check_uri(self, "url", "url")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        pass


class Organization(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        check_uri(self, "@id", "url")

        try:
            check_uri(self, "url", "url")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        pass


class Person(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        check_uri(self, "@id", "url")
        check_email(self, "email")

        try:
            check_phonenumber(self, "telephone")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        pass


class License(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        check_uri(self, "@id", "url")

    def validate(self) -> None:
        # TODO: impl.
        pass


class RepositoryObject(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        check_uri(self, "@id", "url")

    def validate(self) -> None:
        # TODO: impl.
        pass


class DataDownload(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        check_uri(self, "@id", "url")

        try:
            check_sha256(self)
            check_isodate(self, "uploadDate")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        pass


class HostingInstitution(Organization):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    def check_props(self) -> None:
        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        check_uri(self, "@id", "url")

        try:
            check_uri(self, "url", "url")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        pass


class ContactPoint(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        schema = load_entity_def_from_schema_file(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_all_prop_types(self, schema["type_dict"])

        try:
            check_email(self, "email")
            check_phonenumber(self, "telephone")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        pass
