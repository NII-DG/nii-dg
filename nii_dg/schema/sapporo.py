#!/usr/bin/env python3
# coding: utf-8

'''
This schema is for validation of workflow execution using sapporo-service.
For more information about sapporo-service, please see:
https://github.com/sapporo-wes/sapporo-service
'''

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from nii_dg.entity import ContextualEntity
from nii_dg.error import EntityError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import (check_all_prop_types, check_content_formats,
                          check_content_size, check_required_props,
                          check_sha256, check_unexpected_props, classify_uri,
                          download_file_from_url, get_file_sha256,
                          get_sapporo_run_status,
                          load_entity_def_from_schema_file, sum_file_size)

SCHEMA_NAME = Path(__file__).stem
SAPPORO_ENDPOINT = "http://sapporo-service:1122"


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
                prop_errors.add("@id", "The @id value MUST be URL or relative path to the file, not absolute path.")
        except ValueError as error:
            prop_errors.add("@id", str(error))

        try:
            check_content_formats(self, {
                "contentSize": check_content_size,
                "sha256": check_sha256,
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: ROCrate) -> None:
        try:
            super(BaseFile, self).validate(crate)
            validation_failures = EntityError(self)
        except EntityError as ent_err:
            validation_failures = ent_err

        sapporo_run_ents = crate.get_by_entity_type(SapporoRun)
        if len(sapporo_run_ents) == 0:
            validation_failures.add("AnotherEntity", "Entity `SapporoRun` MUST be required with sapporo.File entity.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class SapporoRun(ContextualEntity):
    def __init__(self, id_: str = "#sapporo-run", props: Optional[Dict[str, Any]] = None):
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

        if (len(validation_failures.message_dict.keys() & {"run_request", "sapporo_config"}) > 0):
            raise validation_failures

        if isinstance(self["run_request"], dict):
            self["run_request"] = crate.get_by_id_and_entity_type(self["run_request"]["@id"], File)
        if isinstance(self["sapporo_config"], dict):
            self["sapporo_config"] = crate.get_by_id_and_entity_type(self["sapporo_config"]["@id"], File)

        if "contents" not in self["sapporo_config"]:
            validation_failures.add("sapporo_config", f"""The property `contents` and its value are required in the entity {self["sapporo_config"]}.""")
            raise validation_failures

        endpoint = SAPPORO_ENDPOINT

        if "contents" not in self["run_request"]:
            validation_failures.add("run_request", f"""The property `contents` and its value are required in the entity {self["run_request"]}.""")
            raise validation_failures
        run_request = json.loads(self["run_request"]["contents"])

        try:
            re_exec = requests.post(endpoint + "/runs", data=run_request, timeout=(10.0, 30.0))
            re_exec.raise_for_status()
        except Exception as err:
            validation_failures.add("run_request", f"Failed to re-execute workflow: {err}.")
            validation_failures.add("sapporo_config", f"Failed to re-execute workflow: {err}.")
            raise validation_failures

        run_id = re_exec.json()["run_id"]
        re_exec_status = get_sapporo_run_status(run_id, endpoint)

        if re_exec_status != self["state"]:
            validation_failures.add("state", f"""The status of the workflow execution MUST be {self["state"]}; got {re_exec_status} instead.""")
            raise validation_failures

        if re_exec_status != "COMPLETE":
            if len(validation_failures.message_dict) > 0:
                raise validation_failures
            return
        output_entities = [ent for ent in crate.get_by_entity_type(File) if "outputs/" in ent.id]

        re_exec_results = requests.get(endpoint + "/runs/" + run_id, timeout=(10, 30)).json()
        dir_path = Path.cwd().joinpath("tmp_sapporo", run_id)
        dir_path.mkdir(parents=True)
        file_list = [file_dict["file_name"] for file_dict in re_exec_results["outputs"]]

        for file_name in file_list:
            file_path = dir_path.joinpath(file_name)
            download_file_from_url(endpoint + "/runs/" + run_id + "/data/outputs/" + file_name, file_path)
            file_ent = [ent for ent in output_entities if file_name in ent.id]

            if len(file_ent) == 0:
                validation_failures.add(f"outputs, {file_name}",
                                        f"The file {file_name} is included in the result of re-execution, but not included in this crate.")
                continue

            if "contentSize" in file_ent[0] and os.path.getsize(file_path) != sum_file_size("B", file_ent):
                validation_failures.add(
                    f"outputs, {file_name}:contentSize", f"""The file size of {file_name}, {os.path.getsize(file_path)}B, does not match the `contentSize` value {file_ent[0]["contentSize"]} in {file_ent[0]}.""")

            if "sha256" in file_ent[0] and get_file_sha256(file_path) != file_ent[0]["sha256"]:
                validation_failures.add(
                    f"outputs, {file_name}:sha256", f"""The hash of {file_name} does not match the `sha256` value {file_ent[0]["sha256"]} in {file_ent[0]}""")

        shutil.rmtree(dir_path.parent)
        if len(validation_failures.message_dict) > 0:
            raise validation_failures
