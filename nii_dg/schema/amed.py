#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from nii_dg.check_functions import (check_entity_values, is_absolute_path,
                                    is_iso8601, is_url, is_url_accessible)
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
    def __init__(self, id_: str = "#AMED-DMP", props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["DMPMetadata"]):
        default_props = {
            "name": "AMED-DMP",
        }
        default_props.update(props)
        super().__init__(id_, default_props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "sdDatePublished": is_iso8601,
        })
        if self.id != "#AMED-DMP":
            error.add("@id", "The id MUST be '#AMED-DMP'.")
        if self["name"] != "AMED-DMP":
            error.add("name", "The name MUST be 'AMED-DMP'.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if self["about"] != crate.root and self["about"] != {"@id": "./"}:
            error.add("about", "The value of the about property MUST be the RootDataEntity of this crate.")
        if len(self["hasPart"]) > 0:
            if "creator" not in self:
                error.add("creator", "The creator property is required when the hasPart property is not empty.")
            if "hostingInstitution" not in self:
                error.add("hostingInstitution", "The hostingInstitution property is required when the hasPart property is not empty.")
            if "dataManager" not in self:
                error.add("dataManager", "The dataManager property is required when the hasPart property is not empty.")
        if len(self["hasPart"]) > len(crate.get_by_type("DMP")):
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
                error.add("@id", "The id MUST be '#dmp:<dataNumber>'.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        dmp_metadata_ents = crate.get_by_type("DMPMetadata")
        if len(dmp_metadata_ents) == 0:
            error.add("AnotherEntity", "Entity `DMPMetadata` MUST be required with DMP entity.")
        else:
            dmp_metadata_ent = dmp_metadata_ents[0]
            if "repository" not in [*self.keys(), *dmp_metadata_ent.keys()]:
                error.add("repository", "This property is required, but not found.")

            if self["accessRights"] == "Unrestricted Open Sharing" and "distribution" not in [*self.keys(), *dmp_metadata_ent.keys()]:
                error.add("distribution", "This property is required, but not found.")

        if self["accessRights"] in ["Unshared", "Restricted Closed Sharing"] and\
                not any(map(self.keys().__contains__, ("availabilityStarts", "reasonForConcealment"))):
            error.add("availabilityStarts",
                      "This property is required, but not found. If the dataset remains unshared, add reasonForConcealment property instead.")

        if "availabilityStarts" in self and self["accessRights"] in ["Restricted Open Sharing", "Unrestricted Open Sharing"]:
            error.add("availabilityStarts", "This property is not required because the data is accessible at this time.")

        if self["gotInformedConsent"] == "yes" and "informedConsentFormat" not in self:
            error.add("informedConsentFormat", "This property is required, but not found.")

        if "contentSize" in self:
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
            error.add("@id", "The id MUST be a URL or a relative path.")

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


class ClinicalResearchRegistration(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["ClinicalResearchRegistration"]):
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

        if not is_url_accessible(self.id):
            error.add("@id", "The URL is not accessible.")

        if error.has_error():
            raise error
