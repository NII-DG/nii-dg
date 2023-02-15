#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity
from nii_dg.error import CrateError, EntityError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import (check_all_prop_types, check_content_formats,
                          check_content_size, check_isodate, check_mime_type,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, classify_uri,
                          load_entity_def_from_schema_file, sum_file_size,
                          verify_is_past_date)


class DMPMetadata(ContextualEntity):
    def __init__(self, id: Optional[str] = None, props: Optional[Dict[str, Any]] = None):
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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        if self.id != "#METI-DMP":
            prop_errors.add("@id", "The value MUST be '#METI-DMP'.")

        if self["name"] != "METI-DMP":
            prop_errors.add("name", "The value MUST be 'METI-DMP'.")

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: ROCrate) -> None:
        validation_failures = EntityError(self)

        if self["about"] != crate.root:
            validation_failures.add("about", "The value of this property MUST be the RootDataEntity of this crate.")

        organization = self["funder"]
        if "funder" in crate.root.keys() and organization not in crate.root["funder"]:
            validation_failures.add("funder", f"The entity {organization} is not included in the funder property of RootDataEntity.")

        if len(self["hasPart"]) != len(crate.get_by_entity_type(DMP)):
            diff = []
            for dmp in crate.get_by_entity_type(DMP):
                if dmp not in self["hasPart"]:
                    diff.append(dmp)
            validation_failures.add("hasPart", f"There is an omission of DMP entity in the list: {diff}.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class DMP(ContextualEntity):
    def __init__(self, id: int, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="#dmp:" + str(id), props=props)
        self["dataNumber"] = id

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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            check_content_formats(self, {
                "availabilityStarts": check_isodate
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        try:
            if verify_is_past_date(self, "availabilityStarts"):
                prop_errors.add("availabilityStarts", "The value MUST be the date of future.")
        except (TypeError, ValueError):
            prop_errors.add("availabilityStarts", "The value is invalid date format. MUST be 'YYYY-MM-DD'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: ROCrate) -> None:
        validation_failures = EntityError(self)

        dmp_metadata_ents = crate.get_by_entity_type(DMPMetadata)
        if len(dmp_metadata_ents) == 0:
            raise CrateError("Entity DMPMetadata MUST be required with DMP entity.")

        dmp_metadata_ent = dmp_metadata_ents[0]

        if self["accessRights"] != "open access" and "reasonForConcealment" not in self.keys():
            validation_failures.add("reasonForConcealment", "This property is required, but not found.")

        if self["accessRights"] == "embargoed access" and "availabilityStarts" not in self.keys():
            validation_failures.add("availabilityStarts", "This property is required, but not found.")

        if self["accessRights"] != "embargoed access" and "availabilityStarts" in self.keys():
            validation_failures.add("availabilityStarts", "This property is not required.")

        if verify_is_past_date(self, "availabilityStarts"):
            validation_failures.add("availabilityStarts", "The value MUST be the date of future.")

        if self["accessRights"] in ["open access", "restricted access"] and "isAccessibleForFree" not in self.keys():
            validation_failures.add("isAccessibleForFree", "This property is required, but not found.")

        if self["accessRights"] == "open access":
            if "isAccessibleForFree" in self.keys() and self["isAccessibleForFree"] is False:
                validation_failures.add("isAccessibleForFree", "The value MUST be True.")
            if "license" not in self.keys():
                validation_failures.add("license", "This property is required, but not found.")
            if "contentSize" not in self.keys():
                validation_failures.add("contentSize", "This property is required, but not found.")

        if self["accessRights"] in ["open access", "restricted access", "embargoed access"] and "contactPoint" not in self.keys():
            validation_failures.add("contactPoint", "This property is required, but not found.")

        if "repository" not in list(self.keys()) + list(dmp_metadata_ent.keys()):
            validation_failures.add("repository", "This property is required, but not found.")

        if self["accessRights"] == "open access" and "distribution" not in list(self.keys()) + list(dmp_metadata_ent.keys()):
            validation_failures.add("distribution", "This property is required, but not found.")

        if "contentSize" in self.keys():
            target_files = []
            for ent in crate.get_by_entity_type(File):
                if ent["dmpDataNumber"] == self:
                    target_files.append(ent)

            sum_size = sum_file_size(self["contentSize"][-2:], target_files)

            if self["contentSize"] != "over100GB" and sum_size > int(self["contentSize"][:-2]):
                validation_failures.add("contentSize", "The total file size included in this DMP is larger than the defined size.")

            if self["contentSize"] == "over100GB" and sum_size < 100:
                validation_failures.add("contentSize", "The total file size included in this DMP is smaller than 100GB.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            if classify_uri(self.id) == "abs_path":
                prop_errors.add("@id", "The value MUST be URL or relative path to the file, not absolute path.")
        except ValueError as error:
            prop_errors.add("@id", str(error))

        try:
            check_content_formats(self, {
                "contentSize": check_content_size,
                "url": check_url,
                "sha256": check_sha256,
                "encodingFormat": check_mime_type,
                "sdDatePublished": check_isodate
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        try:
            if verify_is_past_date(self, "sdDatePublished") is False:
                prop_errors.add("sdDatePublished", "The value MUST be the date of past.")
        except (TypeError, ValueError):
            prop_errors.add("sdDatePublished", "The value is invalid date format. MUST be 'YYYY-MM-DD'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: ROCrate) -> None:
        validation_failures = EntityError(self)

        if classify_uri(self.id) == "URL" and "sdDatePublished" not in self.keys():
            validation_failures.add("sdDatePublished", "This property is required, but not found.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures
