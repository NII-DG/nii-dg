#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from nii_dg.check_functions import (check_entity_values, is_absolute_path,
                                    is_iso8601, is_orcid, is_url,
                                    is_url_accessible)
from nii_dg.entity import ContextualEntity, EntityDef
from nii_dg.error import EntityError
from nii_dg.schema.base import File as BaseFile
from nii_dg.schema.base import Person as BasePerson
from nii_dg.utils import load_schema_file, sum_file_size

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve().parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)


class DMPMetadata(ContextualEntity):
    def __init__(self, id_: str = "#CAO-DMP", props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["DMPMetadata"]):
        default_props = {
            "name": "CAO-DMP"
        }
        default_props.update(props)
        super().__init__(id_, default_props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = EntityError(self)

        if self.id != "#CAO-DMP":
            error.add("@id", "The id MUST be '#CAO-DMP'.")
        if self["name"] != "CAO-DMP":
            error.add("name", "The name MUST be 'CAO-DMP'.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if self["about"] != crate.root and self["about"] != {"@id": "./"}:
            error.add("about", "The value of the about property MUST be the RootDataEntity of this crate.")
        if len(self["hasPart"]) != len(crate.get_by_type(DMP)):
            error.add("hasPart", "The number of the hasPart property MUST be equal to the number of DMP entities.")

        if error.has_error():
            raise error


class DMP(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["DMP"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "availabilityStarts": is_iso8601,
        })
        if "dataNumber" in self:
            if self.id != f"#dmp:{self['dataNumber']}":
                error.add("@id", "The value MUST be started with '#dmp:'and then the value of dataNumber property MUST come after it.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        dmp_metadata_ents = crate.get_by_type(DMPMetadata)
        if len(dmp_metadata_ents) == 0:
            error.add("AnotherEntity", "Entity `DMPMetadata` MUST be required with DMP entity.")
        else:
            dmp_metadata_ent = dmp_metadata_ents[0]
            if "repository" not in [*self.keys(), *dmp_metadata_ent.keys()]:
                error.add("repository", "This property is required, but not found.")

            if self["accessRights"] == "open access" and "distribution" not in [*self.keys(), *dmp_metadata_ent.keys()]:
                error.add("distribution", "This property is required, but not found.")

        if self["accessRights"] == "embargoed access" and "availabilityStarts" not in self:
            error.add("availabilityStarts", "This property is required, but not found.")

        if self["accessRights"] != "embargoed access" and "availabilityStarts" in self:
            error.add("availabilityStarts", "This property is not required.")

        if self["accessRights"] in ["open access", "restricted access"] and "isAccessibleForFree" not in self:
            error.add("isAccessibleForFree", "This property is required, but not found.")

        if self["accessRights"] == "open access" and "license" not in self:
            error.add("license", "This property is required, but not found.")

        if "contentSize" in self:
            target_files = []
            for ent in crate.get_by_type(File):
                if ent["dmpDataNumber"] == self:
                    target_files.append(ent)

            sum_size = sum_file_size(self["contentSize"][-2:], target_files)

            if self["contentSize"] != "over100GB" and sum_size > int(self["contentSize"][: -2]):
                error.add("contentSize", "The total file size included in this DMP is larger than the defined size.")

            if self["contentSize"] == "over100GB" and sum_size < 100:
                error.add("contentSize", "The total file size included in this DMP is smaller than 100GB.")

        if error.has_error():
            raise error


class Person(BasePerson):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["Person"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "@id": is_url,
        })
        if self.id.startswith("https://orcid.org/"):
            if is_orcid(self.id) is False:
                error.add("@id", "The value MUST be a valid ORCID.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if not is_url_accessible(self.id):
            error.add("@id", "The value MUST be a valid URL.")

        if error.has_error():
            raise error


class File(BaseFile):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["File"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = EntityError(self)

        if is_absolute_path(self.id):
            error.add("@id", "The value MUST be a URL or a relative path.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if is_url(self.id):
            if "sdDatePublished" not in self:
                error.add("sdDatePublished", "This property is required, but not found.")

        if error.has_error():
            raise error
