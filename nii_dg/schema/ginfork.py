#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity
from nii_dg.error import EntityError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import (check_all_prop_types, check_content_formats,
                          check_content_size, check_isodate, check_mime_type,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, classify_uri,
                          load_entity_def_from_schema_file, sum_file_size,
                          verify_is_past_date)

REQUIRED_DIRECTORIES = {
    "with_code": ["source", "input_data", "output_data"],
    "for_parameters": ["source", "input_data"]
}

SCHEMA_NAME = Path(__file__).stem


class GinMonitoring(ContextualEntity):
    def __init__(self, id_: str = "#ginmonitoring", props: Optional[Dict[str, Any]] = None):
        super().__init__(id_=id_, props=props, schema_name=SCHEMA_NAME)

    def check_props(self) -> None:
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: ROCrate) -> None:
        try:
            super().validate(crate)
            validation_failures = EntityError(self)
        except EntityError as ent_err:
            validation_failures = ent_err

        if self["about"] != crate.root and self["about"] != {"@id": "./"}:
            validation_failures.add("about", "The value of this property MUST be the RootDataEntity of this crate.")

        targets = [ent for ent in crate.get_by_entity_type(File) if ent["experimentPackageFlag"] is True]
        sum_size = sum_file_size(self["contentSize"][-2:], targets)
        if sum_size > int(self["contentSize"][:-2]):
            validation_failures.add("contentSize", "The total file size of ginfork.File labeled as an experimental package is larger than the defined size.")

        dir_paths = [dir.id for dir in crate.get_by_entity_type(Dataset)]

        required_dir_list = [str(Path(experiment_dir).joinpath(dir_name)) + "/" for experiment_dir in self["experimentPackageList"]
                             for dir_name in REQUIRED_DIRECTORIES[self["datasetStructure"]]]
        missing_dirs = [dir_path for dir_path in required_dir_list if dir_path not in dir_paths]
        if len(missing_dirs) > 0:
            validation_failures.add("experimentPackageList", f"Required Dataset entity is missing; @id `{missing_dirs}`.")

        if self["datasetStructure"] == "for_parameters":
            if "parameterExperimentList" not in self:
                validation_failures.add("parameterExperimentList", "This property is required, but not found.")
            else:
                param_dir_list = [str(Path(param_dir_name).joinpath(required_dir_name)) + "/" for param_dir_name in self["parameterExperimentList"]
                                  for required_dir_name in ["output_data", "params"]]
                missing_param_dirs = [param_dir_path for param_dir_path in param_dir_list if param_dir_path not in dir_paths]
                if len(missing_param_dirs) > 0:
                    validation_failures.add("parameterExperimentList", f"Required Dataset entity is missing; @id `{missing_param_dirs}`.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class File(BaseFile):
    def __init__(self, id_: str, props: Optional[Dict[str, Any]] = None):
        super(BaseFile, self).__init__(id_=id_, props=props, schema_name=SCHEMA_NAME)

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
                "encodingFormat": check_mime_type,
                "url": check_url,
                "sha256": check_sha256,
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
        try:
            super(BaseFile, self).validate(crate)
            validation_failures = EntityError(self)
        except EntityError as ent_err:
            validation_failures = ent_err

        if classify_uri(self.id) == "URL" and "sdDatePublished" not in self.keys():
            validation_failures.add("sdDatePublished", "This property is required, but not found.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures
