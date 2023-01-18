#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity
from nii_dg.error import GovernanceError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import (check_all_prop_types, check_content_formats,
                          check_content_size, check_isodate, check_mime_type,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, classify_uri,
                          load_entity_def_from_schema_file,
                          verify_is_past_date)


class DMPMetadata(ContextualEntity):
    def __init__(self, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="#METI-DMP", props=props)
        self["name"] = "METI-DMP"

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

        if self.id != "#METI-DMP":
            raise PropsError(f"The value of @id property of {self} MUST be '#METI-DMP'.")
        if self["name"] != "METI-DMP":
            raise PropsError(f"The value of name property of {self} MUST be 'METI-DMP'.")
        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

    def validate(self, rocrate: ROCrate) -> None:
        pass


class DMP(ContextualEntity):
    def __init__(self, id: int, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="#dmp:" + str(id), props=props)

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
            "availabilityStarts": check_isodate
        })

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")
        if verify_is_past_date(self, "availabilityStarts"):
            raise PropsError(f"The value of availabilityStarts property of {self} MUST be the date of future.")

    def validate(self, rocrate: ROCrate) -> None:

        if self["accessRights"] != "open access" and "reasonForConcealment" not in self.keys():
            raise GovernanceError(f"A reasonForConcealment property is required in {self}.")
        if self["accessRights"] == "embargoed access" and "availabilityStarts" not in self.keys():
            raise GovernanceError(f"An availabilityStarts property is required in {self}.")
        if verify_is_past_date(self, "availabilityStarts"):
            raise GovernanceError(f"The value of availabilityStarts property of {self} MUST be the date of future.")

        if self["accessRights"] in ["open access", "restricted access"] and "isAccessibleForFree" not in self.keys():
            raise GovernanceError(f"An isAccessibleForFree property is required in {self}.")
        if self["accessRights"] == "open access" and "license" not in self.keys():
            raise GovernanceError(f"A license property is required in {self}.")
        if self["accessRights"] in ["open access", "restricted access"] and "contactPoint" not in self.keys():
            raise GovernanceError(f"A contactPoint property is required in {self}.")

        dmp_metadata_ents = rocrate.get_by_entity_type(DMPMetadata)
        if len(dmp_metadata_ents) == 0:
            raise GovernanceError("DMPMetadata Entity MUST be required with DMP entity.")

        if "repository" not in self.keys():
            # DMPMetadata entity must have the property instead of DMP entity
            if "repository" not in dmp_metadata_ents[0].keys():
                raise GovernanceError(f"A repository property is required in {self}.")

        if self["accessRights"] == "open access" and "distribution" not in self.keys():
            # DMPMetadata entity must have the property instead of DMP entity
            if "distribution" not in dmp_metadata_ents[0].keys():
                raise GovernanceError(f"A distribution property is required in {self}.")

        if "contentSize" in self.keys():
            monitor_file_size(rocrate, self)


class File(BaseFile):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

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
            raise PropsError(f"The value of sdDatePublished property of {self} MUST be the date of past.")
        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

    def validate(self, rocrate: ROCrate) -> None:
        if classify_uri(self, "@id") == "url":
            if "sdDatePublished" not in self.keys():
                raise GovernanceError(f"A sdDatePublished property is required in {self}.")


def monitor_file_size(rocrate: ROCrate, entity: DMP) -> None:
    """
    File size sum が規定値に合っていることを確認
    """
    size = entity["contentSize"]
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit = units.index(size[-2:])

    file_size_sum: float = 0
    for ent in rocrate.get_by_entity_type(File):
        if ent["dmpDataNumber"] != entity:
            continue

        if ent["contentSize"][-2:] in units:
            file_unit = units.index(ent["contentSize"][-2:])
            file_size = int(ent["contentSize"][:-2])
        else:
            file_unit = 0
            file_size = int(ent["contentSize"][:-1])

        file_size_sum += round(file_size / 1024 ** (unit - file_unit), 3)

    if size != "over100GB" and file_size_sum > int(size[:-2]):
        raise GovernanceError(f"The total file size included in DMP {entity} is larger than the defined size.")
    if size == "over100GB" and file_size_sum < 100:
        raise GovernanceError(f"The total file size included in DMP {entity} is smaller than 100GB.")
