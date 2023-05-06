#!/usr/bin/env python3
# coding: utf-8

'''\
This schema is for validation of workflow execution using sapporo-service.
For more information about sapporo-service, please see https://github.com/sapporo-wes/sapporo-service
'''

import argparse
import json
import logging
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import requests

from nii_dg.check_functions import (check_entity_values, is_absolute_path,
                                    is_iso8601, is_relative_path, is_url)
from nii_dg.entity import ContextualEntity, Entity, EntityDef
from nii_dg.error import EntityError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset as BaseDataset
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import (check_all_prop_types, check_content_formats,
                          check_content_size, check_required_props,
                          check_sha256, check_unexpected_props, check_url,
                          classify_uri, download_file_from_url,
                          get_file_sha256, load_entity_def_from_schema_file,
                          load_schema_file, sum_file_size)

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve().parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)

flask_log = logging.getLogger("flask.app")


class File(BaseFile):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["File"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        # contentSize, encodingFormat, sha256, url, sdDatePublished are checked in base class
        super().check_props()

        error = EntityError(self)
        if is_absolute_path(self.id):
            error.add("@id", "The @id value MUST be URL or relative path to the file, not absolute path.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        sapporo_run_ents = crate.get_by_type("SapporoRun")
        if len(sapporo_run_ents) == 0:
            error.add("AnotherEntity", "Entity `SapporoRun` MUST be required with sapporo.File entity.")

        if error.has_error():
            raise error


class Dataset(BaseDataset):
    def __init__(self, id_: str, props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["Dataset"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = EntityError(self)

        if not self.id.endswith("/"):
            error.add("@id", "The value MUST end with '/'.")
        if is_relative_path(self.id):
            error.add("@id", "The value MUST be relative path to the directory, neither absolute path nor URL.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        sapporo_run_ents = crate.get_by_type("SapporoRun")
        if len(sapporo_run_ents) == 0:
            error.add("AnotherEntity", "Entity `SapporoRun` MUST be required with sapporo.File entity.")

        if error.has_error():
            raise error


class SapporoRun(ContextualEntity):
    def __init__(self, id_: str = "#sapporo-run", props: Dict[str, Any] = {},
                 schema_name: str = SCHEMA_NAME,
                 entity_def: EntityDef = SCHEMA_DEF["SapporoRun"]):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(self, {
            "workflow_url": is_url,
            "sapporo_location": is_url,
        })

        if error.has_error():
            raise error

    @classmethod
    def generate_run_request_json(cls, sapporo_run: "SapporoRun") -> Dict[str, Optional[str]]:
        request_keys = ["workflow_params", "workflow_type", "workflow_type_version", "tags", "workflow_engine_name",
                        "workflow_engine_parameters", "workflow_url", "workflow_name", "workflow_attachment"]
        run_request: Dict[str, Optional[str]] = {key: None for key in request_keys}
        for key in request_keys:
            if key in sapporo_run:
                run_request[key] = sapporo_run[key]

        return run_request

    @classmethod
    def execute_wf(cls, sapporo: "SapporoRun") -> str:
        pass

    @classmethod
    def get_run_status(cls, sapporo: "SapporoRun") -> str:
        pass

    def validate(self, crate: ROCrate) -> None:
        super().validate(crate)

        error = EntityError(self)

        endpoint = self["sapporo_location"]
        run_request = self.generate_run_request_json(self)

        data = urlencode(run_request).encode("utf-8")  # type: ignore
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # remove trailing slash from endpoint
        request = Request(f"{endpoint.rstrip('/')}/runs", data=data, headers=headers)  # type: ignore

        with urlopen(request) as response:
            result = json.load(response)
            print(result)

        # try:
        #     re_exec = requests.post(endpoint + "/runs", data=run_request, timeout=(10.0, 30.0))
        #     re_exec.raise_for_status()
        # except Exception as err:
        #     validation_failures.add("sapporo_location", f"Failed to re-execute workflow: {err}.")
        #     raise validation_failures from None

        flask_log.info("Re-execute request to sapporo is accepted successfully in SapporoRun.validate().")
        run_id = re_exec.json()["run_id"]

        try:
            re_exec_status = get_sapporo_run_status(run_id, endpoint)
        except TimeoutError as err:
            validation_failures.add("sapporo_location", f"Failed to get status of re-execution: {err}.")
            raise validation_failures from None

        if re_exec_status != self["state"]:
            validation_failures.add("state", f"""The status of the workflow execution MUST be {self["state"]}; got {re_exec_status} instead.""")
            raise validation_failures

        if re_exec_status != "COMPLETE":
            if len(validation_failures.message_dict) > 0:
                raise validation_failures
            return

        if isinstance(self["outputs"], dict):
            self["outputs"] = crate.get_by_id_and_entity_type(self["outputs"]["@id"], Dataset)

        output_entities: List[Entity] = []
        for ent in self["outputs"]["hasPart"]:
            if isinstance(ent, dict) and crate.get_by_id_and_entity_type(ent["@id"], File):
                output_entities.append(crate.get_by_id_and_entity_type(ent["@id"], File))  # type:ignore
            elif isinstance(ent, File):
                output_entities.append(ent)

        re_exec_results = requests.get(endpoint + "/runs/" + run_id, timeout=(10, 30)).json()
        dir_path = Path.cwd().joinpath("tmp_sapporo", run_id)
        dir_path.mkdir(parents=True)
        file_list = [file_dict["file_name"] for file_dict in re_exec_results["outputs"]]

        for file_name in file_list:
            file_path = dir_path.joinpath(file_name)
            download_file_from_url(endpoint + "/runs/" + run_id + "/data/outputs/" + file_name, file_path)
            file_ent = [ent for ent in output_entities if file_name == ent["name"]]

            if len(file_ent) == 0:
                validation_failures.add(f"outputs_{file_name}",
                                        f"The file {file_name} is included in the result of re-execution, so File entity with @id {file_name} is required in this crate.")
                continue

            if "contentSize" in file_ent[0] and os.path.getsize(file_path) != sum_file_size("B", file_ent):
                validation_failures.add(
                    f"outputs_{file_name}", f"""The file size of {file_name}, {os.path.getsize(file_path)}B, does not match the `contentSize` value {file_ent[0]["contentSize"]} in {file_ent[0]}.""")

            if "sha256" in file_ent[0] and get_file_sha256(file_path) != file_ent[0]["sha256"]:
                validation_failures.add(
                    f"outputs_{file_name}", f"""The hash of {file_name} does not match the `sha256` value {file_ent[0]["sha256"]} in {file_ent[0]}""")

        shutil.rmtree(dir_path.parent)
        if len(validation_failures.message_dict) > 0:
            raise validation_failures
