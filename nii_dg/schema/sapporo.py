#!/usr/bin/env python3
# coding: utf-8

'''
This schema is for validation of workflow execution using sapporo-service.
For more information about sapporo-service, please see:
https://github.com/sapporo-wes/sapporo-service
'''

import json
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
                          download_file_from_url, get_sapporo_run_status,
                          load_entity_def_from_schema_file)

SCHEMA_NAME = Path(__file__).stem


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

        if (len(validation_failures.message_dict.keys() & {"run_request""sapporo_config"}) > 0):
            raise validation_failures

        if isinstance(self["run_request"], dict):
            self["run_request"] = crate.get_by_id_and_entity_type(self["run_request"]["@id"], File)
        if isinstance(self["sapporo_config"], dict):
            self["sapporo_config"] = crate.get_by_id_and_entity_type(self["sapporo_config"]["@id"], File)

        if "contents" not in self["sapporo_config"]:
            validation_failures.add("sapporo_config", f"""The property `contents` and its value are required in the entity {self["sapporo_config"]}.""")
            raise validation_failures
        config = json.loads(self["sapporo_config"]["contents"])

        if "sapporo_endpoint" not in config:
            validation_failures.add("sapporo_config", "The property `sapporo_endpoint` and its value are required in the contents.")
            raise validation_failures
        endpoint = config["sapporo_endpoint"]

        if "contents" not in self["run_request"]:
            validation_failures.add("run_request", f"""The property `contents` and its value are required in the entity {self["run_request"]}.""")
            raise validation_failures
        run_request = json.loads(self["run_request"]["contents"])

        try:
            print("request run")
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

        re_exec_results = requests.get(endpoint + "/runs/" + run_id, timeout=(10, 30)).json()
        dir_path = Path.cwd().joinpath("tmp_sapporo", run_id)
        dir_path.mkdir(parents=True)
        file_list = [file_dict["file_name"] for file_dict in re_exec_results["outputs"]]
        for file_name in file_list:
            download_file_from_url(endpoint + "/runs/" + run_id + "/data/outputs/" + file_name, str(dir_path.joinpath(file_name)))

        if len(validation_failures.message_dict) > 0:
            raise validation_failures
