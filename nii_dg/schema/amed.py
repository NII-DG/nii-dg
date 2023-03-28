#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from urllib.request import urlopen

from nii_dg.check_functions import (check_entity_values, is_content_size,
                                    is_email, is_encoding_format, is_iso8601,
                                    is_orcid, is_phone_number,
                                    is_relative_path, is_sha256, is_url,
                                    is_url_accessible)
from nii_dg.entity import ContextualEntity, DataEntity, EntityDef
from nii_dg.error import EntityError
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import load_schema_file

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve().parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)


class DMPMetadata(ContextualEntity):
    def __init__(self, id_: str = "#AMED-DMP", props: Dict[str, Any] = {"name": "AMED-DMP"},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["DMPMetadata"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "sdDatePublished": is_iso8601,
        })
        if self.id != "#AMED-DMP":
            error.add("id", "The id MUST be '#AMED-DMP'.")
        if self["name"] != "AMED-DMP":
            error.add("name", "The name MUST be 'AMED-DMP'.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        error = EntityError(self)
        if self["about"] != crate.root and self["about"] != {"@id": "./"}:
            error.add("about", "The value of the about property MUST be the RootDataEntity of this crate.")
        if len(self["hasPart"]) > 0:
            if self.get("creator") is None:
                error.add("creator", "The creator property is required when the hasPart property is not empty.")
            if self.get("hostingInstitution") is None:
                error.add("hostingInstitution", "The hostingInstitution property is required when the hasPart property is not empty.")
            if self.get("dataManager") is None:
                error.add("dataManager", "The dataManager property is required when the hasPart property is not empty.")

        if error.has_error():
            raise error


class DMP(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["DMP"]):
        super().__init__(id_, props, schema_name, entity_def)


class File(BaseFile):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["File"]):
        super().__init__(id_, props, schema_name, entity_def)


class ClinicalResearchRegistration(ContextualEntity):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["ClinicalResearchRegistration"]):
        super().__init__(id_, props, schema_name, entity_def)
