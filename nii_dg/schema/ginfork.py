#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from nii_dg.check_functions import is_absolute_path, is_url
from nii_dg.entity import ContextualEntity, EntityDef
from nii_dg.error import EntityError
from nii_dg.schema.base import Dataset
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import load_schema_file, sum_file_size

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve(
).parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)


class GinMonitoring(ContextualEntity):
    REQUIRED_DIRECTORIES = {
        "with_code": ["source", "input_data", "output_data"],
        "for_parameters": ["source", "input_data"]
    }

    def __init__(self, id_: str = "#ginmonitoring", props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["GinMonitoring"]):
        default_props = {
            "name": "ginmonitoring",
        }
        default_props.update(props)
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if self["about"] != crate.root and self["about"] != {"@id": "./"}:
            error.add(
                "about", "The value of this property MUST be the RootDataEntity of this crate.")

        targets = [ent for ent in crate.get_by_type(File) if ent["experimentPackageFlag"] is True]
        sum_size = sum_file_size(self["contentSize"][-2:], targets)
        if sum_size > int(self["contentSize"][:-2]):
            error.add(
                "contentSize", "The total file size of ginfork.File labeled as an experimental package is larger than the defined size.")

        dir_paths = [Path(dir_.id) for dir_ in crate.get_by_type(Dataset)]
        required_dirs = [Path(experiment_dir).joinpath(required_dir_name)
                         for experiment_dir in self["experimentPackageList"]
                         for required_dir_name in self.REQUIRED_DIRECTORIES[self["datasetStructure"]]]
        missing_dirs = [
            dir_path for dir_path in required_dirs if dir_path not in dir_paths]
        if len(missing_dirs) > 0:
            error.add("experimentPackageList",
                      f"Required Dataset entity is missing; @id '{missing_dirs}'.")

        if self["datasetStructure"] == "for_parameters":
            if "parameterExperimentList" not in self:
                error.add("parameterExperimentList",
                          "This property is required, but not found.")
            else:
                param_dirs = [Path(param_dir).joinpath(required_dir_name)
                              for param_dir in self["parameterExperimentList"]
                              for required_dir_name in ["output_data", "params"]]
                missing_dirs = [
                    param_dir for param_dir in param_dirs if param_dir not in dir_paths]
                if len(missing_dirs) > 0:
                    error.add("parameterExperimentList",
                              f"Required Dataset entity is missing; @id '{missing_dirs}'.")

        if error.has_error():
            raise error


class File(BaseFile):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["File"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        # "contentSize", "encodingFormat", "url", "sha256", "sdDatePublished" are checked in super().check_props()
        super().check_props()

        error = EntityError(self)

        if is_absolute_path(self.id):
            error.add(
                "@id", "The value MUST be URL or relative path to the file, not absolute path.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if is_url(self.id):
            if "sdDatePublished" not in self:
                error.add("sdDatePublished",
                          "This property is required, but not found.")

        if error.has_error():
            raise error
