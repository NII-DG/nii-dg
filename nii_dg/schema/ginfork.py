#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from nii_dg.check_functions import is_absolute_path, is_url
from nii_dg.entity import ContextualEntity, EntityDef
from nii_dg.error import EntityError
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import load_schema_file, sum_file_size

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve().parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)

REQUIRED_DIRECTORIES = {
    "with_code": ["source", "input_data", "output_data"],
    "for_parameter": ["source", "input_data"]
}


class GinMonitoring(ContextualEntity):
    def __init__(self, id_: str = "#ginmonitoring", props: Dict[str, Any] = {"name": "ginmonitoring"},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["GinMonitoring"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

    def validate(self, crate: "ROCrate") -> None:
        error = EntityError(self)

        if self["about"] != crate.root and self["about"] != {"@id": "./"}:
            error.add("about", "The value of this property MUST be the RootDataEntity of this crate.")

        targets = [ent for ent in crate.get_by_type("File") if ent["experimentPackageFlag"] is True]
        sum_size = sum_file_size(self["contentSize"][-2:], targets)
        if sum_size > int(self["contentSize"][:-2]):
            error.add("contentSize", "The total file size of ginfork.File labeled as an experimental package is larger than the defined size.")

        dir_paths = [dir.id for dir in crate.get_by_type("Dataset")]
        missing_dirs = []
        for dir_name in REQUIRED_DIRECTORIES[self["datasetStructure"]]:
            if dir_name not in [path.split('/')[-2] for path in dir_paths]:
                missing_dirs.append(dir_name)

        if len(missing_dirs) > 0:
            error.add("datasetStructure", f"Couldn't find required directories: named {missing_dirs}.")

        # TODO: update file name rules
        parent_dirs = {dir_name: [path[: -(len(dir_name) + 1)] for path in dir_paths if path.split('/')[-2] == dir_name]
                       for dir_name in ["source", "input_data", "output_data"]}
        if self["datasetStructure"] == "for_parameter" and len(set(parent_dirs["source"]) & set(parent_dirs["input_data"])) == 0:
            error.add("datasetStructure", "The parent directories of source dir and input dir are not the same.")
        if self["datasetStructure"] == "with_code" and\
                len(set(parent_dirs["source"]) & set(parent_dirs["input_data"]) & set(parent_dirs["output_data"])) == 0:
            error.add("datasetStructure", "The parent directories of source dir, input dir and output dir are not the same.")

        if error.has_error():
            raise error


class File(BaseFile):
    def __init__(self, id_: str = "#file", props: Dict[str, Any] = {"name": "file"},
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
        error = EntityError(self)
        if is_url(self.id):
            if "sdDatePublished" not in self:
                error.add("sdDatePublished", "This property is required, but not found.")

        if error.has_error():
            raise error
