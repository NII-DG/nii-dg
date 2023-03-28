#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from nii_dg.check_functions import (check_entity_values, is_absolute_path,
                                    is_iso8601, is_url)
from nii_dg.entity import ContextualEntity, EntityDef
from nii_dg.error import EntityError
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import load_schema_file, sum_file_size

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve().parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)


class DMPMetadata(ContextualEntity):
    def __init__(self, id_: str = "#METI-DMP", props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["DMPMetadata"]):
        default_props = {
            "name": "METI-DMP"
        }
        default_props.update(props)
        super().__init__(id_, default_props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = EntityError(self)
        if self.id != "#METI-DMP":
            error.add("id", "The id MUST be '#METI-DMP'.")
        if self["name"] != "METI-DMP":
            error.add("name", "The name MUST be 'METI-DMP'.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        error = EntityError(self)
        if self["about"] != crate.root and self["about"] != {"@id": "./"}:
            error.add("about", "The value of this property MUST be the RootDataEntity of this crate.")
        if len(self["hasPart"]) != len(crate.get_by_type("DMP")):
            diff = []
            for dmp in crate.get_by_type("DMP"):
                if dmp not in self["hasPart"]:
                    diff.append(dmp)
            error.add("hasPart", f"There is an omission of DMP entity in the list: {diff}.")

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
                error.add("id", "The id MUST be '#dmp:{dataNumber}'.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        error = EntityError(self)

        dmp_metadata_ents = crate.get_by_type("DMPMetadata")
        if len(dmp_metadata_ents) == 0:
            error.add("AnotherEntity", "Entity 'DMPMetadata' MUST be required with DMP entity.")
        else:
            dmp_metadata_ent = dmp_metadata_ents[0]
            if "repository" not in list(self.keys()) + list(dmp_metadata_ent.keys()):
                error.add("repository", "This property is required, but not found.")

            if self["accessRights"] == "open access" and "distribution" not in list(self.keys()) + list(dmp_metadata_ent.keys()):
                error.add("distribution", "This property is required, but not found.")

        if self["accessRights"] != "open access" and "reasonForConcealment" not in self.keys():
            error.add("reasonForConcealment", "This property is required, but not found.")

        if self["accessRights"] == "embargoed access" and "availabilityStarts" not in self.keys():
            error.add("availabilityStarts", "This property is required, but not found.")

        if self["accessRights"] != "embargoed access" and "availabilityStarts" in self.keys():
            error.add("availabilityStarts", "This property is not required.")

        if self["accessRights"] in ["open access", "restricted access"] and "isAccessibleForFree" not in self.keys():
            error.add("isAccessibleForFree", "This property is required, but not found.")

        if self["accessRights"] == "open access":
            if "isAccessibleForFree" in self.keys() and self["isAccessibleForFree"] is False:
                error.add("isAccessibleForFree", "The value MUST be True.")
            if "license" not in self.keys():
                error.add("license", "This property is required, but not found.")
            if "contentSize" not in self.keys():
                error.add("contentSize", "This property is required, but not found.")

        if self["accessRights"] in ["open access", "restricted access", "embargoed access"] and "contactPoint" not in self.keys():
            error.add("contactPoint", "This property is required, but not found.")

        if "contentSize" in self.keys():
            target_files = []
            for ent in crate.get_by_type("File"):
                if ent["dmpDataNumber"] == self:
                    target_files.append(ent)

            sum_size = sum_file_size(self["contentSize"][-2:], target_files)

            if self["contentSize"] != "over100GB" and sum_size > int(self["contentSize"][:-2]):
                error.add("contentSize", "The total file size included in this DMP is larger than the defined size.")

            if self["contentSize"] == "over100GB" and sum_size < 100:
                error.add("contentSize", "The total file size included in this DMP is smaller than 100GB.")

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
            error.add("id", "The id MUST be a URL or a relative path.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        error = EntityError(self)

        if is_url(self.id):
            if "sdDatePublished" not in self:
                error.add("sdDatePublished", "This property is required, but not found.")

        if error.has_error():
            raise error
