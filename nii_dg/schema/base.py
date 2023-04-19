#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from urllib.request import urlopen

from nii_dg.check_functions import (check_entity_values, is_absolute_path,
                                    is_content_size, is_email,
                                    is_encoding_format, is_iso8601, is_orcid,
                                    is_phone_number, is_relative_path,
                                    is_sha256, is_url, is_url_accessible)
from nii_dg.entity import ContextualEntity, DataEntity, EntityDef
from nii_dg.error import EntityError
from nii_dg.utils import load_schema_file

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve().parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)


class File(DataEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["File"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "contentSize": is_content_size,
            "encodingFormat": is_encoding_format,
            "sha256": is_sha256,
            "url": is_url,
            "sdDatePublished": is_iso8601,
        })
        if is_absolute_path(self.id):
            error.add("@id", "The id MUST be a URL or a relative path.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)
        if is_url(self.id):
            if "sdDataPublished" not in self:
                error.add("sdDataPublished", "The property `sdDataPublished` is required when the id is a URL.")

        if error.has_error():
            raise error


class Dataset(DataEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["Dataset"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "url": is_url,
        })
        if not self.id.endswith("/"):
            error.add("@id", "The id MUST end with `/`.")
        if not is_relative_path(self.id):
            error.add("@id", "The id MUST be a relative path.")

        if error.has_error():
            raise error


class Organization(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["Organization"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "@id": is_url,
            "url": is_url,
        })

        if error.has_error():
            raise error

    @classmethod
    def fetch_organization_names_from_ror_api(cls, ror_id: str) -> List[str]:
        """\
        Fetch organization names from ROR API.

        Raises:
            urllib.error.HTTPError: If the ROR API returns an error.
        """
        with urlopen(f"https://api.ror.org/organizations/{ror_id}") as res:
            json = res.read().decode("utf-8")
            name_list = [json["name"]]
            name_list.extend(json["aliases"])

        return name_list

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if self.id.startswith("https://ror.org/"):
            ror_id = self.id.replace("https://ror.org/", "")
            name_list = self.fetch_organization_names_from_ror_api(ror_id)
            if self["name"] not in name_list:
                error.add("name", f"The name MUST be one of {name_list} registered in ROR.")
        else:
            if is_url_accessible(self.id):
                error.add("@id", "Failed to access the URL.")

        if error.has_error():
            raise error


class Person(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["Person"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "@id": is_url,
            "email": is_email,
            "telephone": is_phone_number,
        })
        if str(self.id).startswith("https://orcid.org/"):
            if is_orcid(str(self.id).replace("https://orcid.org/", "")):
                error.add("@id", "The id MUST be a valid ORCID.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if is_url_accessible(self.id):
            error.add("@id", "Failed to access the URL.")

        if error.has_error():
            raise error


class License(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["License"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "@id": is_url,
        })

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if is_url_accessible(self.id):
            error.add("@id", "Failed to access the URL.")

        if error.has_error():
            raise error


class RepositoryObject(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["RepositoryObject"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "@id": is_url,
        })

        if error.has_error():
            raise error


class DataDownload(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["DataDownload"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "@id": is_url,
            "sha256": is_sha256,
            "uploadDate": is_iso8601,
        })

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if is_url_accessible(self.id):
            error.add("@id", "Failed to access the URL.")

        if error.has_error():
            raise error


class HostingInstitution(Organization):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["HostingInstitution"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        # Checked @id and url in Organization.check_props()
        super().check_props()

    def validate(self, crate: "ROCrate") -> None:
        # Checked ROR ID in Organization.validate()
        super().validate(crate)


class ContactPoint(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["ContactPoint"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "email": is_email,
            "telephone": is_phone_number,
        })
        if not self.id.startswith("#mailto:") and not self.id.startswith("#callto:"):
            error.add("@id", "The id MUST start with '#mailto:' or '#callto:'.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if self.id.startswith("#mailto:"):
            email = self.id.replace("#mailto:", "")
            if self.get("email") is None:
                error.add("email", "This property is required.")
            elif self.get("email") != email:
                error.add("@id", "The email address MUST be the same as the value of the email property.")
                error.add("email", "The email address MUST be the same as the value of the @id property.")
        elif self.id.startswith("#callto:"):
            phone_number = self.id.replace("#callto:", "")
            if self.get("telephone") is None:
                error.add("telephone", "This property is required.")
            elif self.get("telephone") != phone_number:
                error.add("@id", "The phone number MUST be the same as the value of the telephone property.")
                error.add("telephone", "The phone number MUST be the same as the value of the @id property.")

        if error.has_error():
            raise error
