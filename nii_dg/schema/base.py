#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity, DataEntity, DefaultEntity
from nii_dg.error import GovernanceError, PropsError
from nii_dg.utils import (EntityDef, access_url, check_all_prop_types,
                          check_content_formats, check_content_size,
                          check_email, check_isodate, check_mime_type,
                          check_orcid_id, check_phonenumber,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, classify_uri,
                          get_name_from_ror, github_branch, github_repo,
                          load_entity_def_from_schema_file,
                          verify_is_past_date)


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
            schema=self.schema_name,
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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)
        entity_def_of_root: EntityDef = {prop: obj for prop, obj in entity_def.items() if prop not in ["dateCreated", "hasPart"]}  # type: ignore

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def_of_root)
        check_all_prop_types(self, entity_def)

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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        if classify_uri(self, "@id") == "abs_path":
            raise PropsError(f"The @id value in {self} MUST be URL or relative path to the file, not absolute path.")

        check_content_formats(self, {
            "contentSize": check_content_size,
            "url": check_url,
            "sha256": check_sha256,
            "encodingFormat": check_mime_type,
            "sdDatePublished": check_isodate
        })

        if verify_is_past_date(self, "sdDatePublished") is False:
            raise PropsError("The value of sdDatePublished MUST not be the date of future.")

    def validate(self) -> None:
        if classify_uri(self, "@id") == "url":
            if "sdDatePublished" not in self.keys():
                raise GovernanceError(f"The property sdDatePublished MUST be included in {self}.")


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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        if not self["@id"].endswith("/"):
            raise PropsError(f"The @id value in {self} MUST end with '/'.")
        if classify_uri(self, "@id") != "rel_path":
            raise PropsError(f"The @id value in {self} MUST be relative path to the directory, neither absolute path nor URL.")

        check_content_formats(self, {
            "url": check_url
        })

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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url,
            "url": check_url
        })

    def validate(self) -> None:
        if self.id.startswith("https://ror.org/"):
            ror_namelist = get_name_from_ror(self.id[16:])
            if self["name"] not in ror_namelist:
                raise GovernanceError(f"The value of name property in {self} MUST be same as the registered name in ROR.")
        else:
            access_url(self.id)


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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url,
            "email": check_email,
            "telephone": check_phonenumber
        })

        if self.id.startswith("https://orcid.org/"):
            check_orcid_id(self.id[18:])

    def validate(self) -> None:
        access_url(self.id)


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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url
        })

    def validate(self) -> None:
        access_url(self.id)


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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url
        })

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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url,
            "sha256": check_sha256,
            "uploadDate": check_isodate
        })

    def validate(self) -> None:
        access_url(self.id)


class HostingInstitution(Organization):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    def check_props(self) -> None:
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url,
            "url": check_url
        })

    def validate(self) -> None:
        super().validate()


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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "email": check_email,
            "telephone": check_phonenumber
        })

    def validate(self) -> None:
        if any(map(self.keys().__contains__, ("email", "telephone"))) is False:
            raise GovernanceError(f"Either property email or telephone is required in {self}.")
