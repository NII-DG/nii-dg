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
    "for_parameter": ["source", "input_data"]
}


class GinMonitoring(ContextualEntity):
    def __init__(self, id: int, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="#ginmonitoring:" + str(id), props=props)

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

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: ROCrate) -> None:
        # TODO: impl.
        validation_failures = EntityError(self)

        if self["about"] != crate.root:
            validation_failures.add("about", "The value of this property MUST be the RootDataEntity of this crate.")

        targets = [ent for ent in crate.get_by_entity_type(File) if ent["experimentPackageFlag"] is True]
        sum = sum_file_size(self["contentSize"][-2:], targets)
        if sum > int(self["contentSize"][:-2]):
            validation_failures.add("contentSize", "The total file size of ginfork.File labeled as an experimental package is larger than the defined size.")

        dir_paths = [dir.id for dir in crate.get_by_entity_type(Dataset)]
        missing_dirs = []
        for dir_name in REQUIRED_DIRECTORIES[self["datasetStructure"]]:
            if dir_name not in [path.split('/')[-2] for path in dir_paths]:
                missing_dirs.append(dir_name)

        if len(missing_dirs) > 0:
            validation_failures.add("datasetStructure", f"Couldn't find required directories: named {missing_dirs}.")

        parent_dirs = {dir_name: [path[: -(len(dir_name) + 1)] for path in dir_paths if path.split('/')[-2] == dir_name]
                       for dir_name in ["source", "input_data", "output_data"]}
        if self["datasetStructure"] == "for_parameter" and len(set(parent_dirs["source"]) & set(parent_dirs["input_data"])) == 0:
            validation_failures.add("datasetStructure", "The parent directories of source dir and input dir are not the same.")
        if self["datasetStructure"] == "with_code" and\
                len(set(parent_dirs["source"]) & set(parent_dirs["input_data"]) & set(parent_dirs["output_data"])) == 0:
            validation_failures.add("datasetStructure", "The parent directories of source dir, input dir and output dir are not the same.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class File(BaseFile):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @ property
    def schema_name(self) -> str:
        return Path(__file__).stem

    @ property
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

        if classify_uri(self, "@id") == "abs_path":
            prop_errors.add("@id", "The value MUST be URL or relative path to the file, not absolute path.")

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
        except PropsError as e:
            prop_errors.add("sdDatePublished", str(e))

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: ROCrate) -> None:
        # TODO: impl.
        pass
