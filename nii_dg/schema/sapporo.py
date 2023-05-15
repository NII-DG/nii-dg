#!/usr/bin/env python3
# coding: utf-8

'''\
This schema is for validation of workflow execution using sapporo-service.
For more information about sapporo-service, please see https://github.com/sapporo-wes/sapporo-service
'''

import hashlib
import json
import logging
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from nii_dg.check_functions import (check_entity_values, is_absolute_path,
                                    is_relative_path, is_url)
from nii_dg.entity import ContextualEntity, Entity, EntityDef
from nii_dg.error import EntityError
from nii_dg.schema.base import Dataset as BaseDataset
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import load_schema_file

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

        sapporo_run_ents = crate.get_by_type(SapporoRun)
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
        if not is_relative_path(self.id):
            error.add("@id", "The value MUST be relative path to the directory, neither absolute path nor URL.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        sapporo_run_ents = crate.get_by_type(SapporoRun)
        if len(sapporo_run_ents) == 0:
            error.add("AnotherEntity", "Entity `SapporoRun` MUST be required with sapporo.File entity.")

        if error.has_error():
            raise error


class SapporoRun(ContextualEntity):
    RUNNING = ["QUEUED", "INITIALIZING", "RUNNING", "PAUSED"]
    COMPLETE = ["COMPLETE"]
    FAILED = ["EXECUTOR_ERROR", "SYSTEM_ERROR", "CANCELED", "CANCELING", "UNKNOWN"]

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
    def generate_run_request_json(cls, sapporo_run: "SapporoRun") -> Dict[str, str]:
        request_keys = ["workflow_params", "workflow_type", "workflow_type_version", "tags", "workflow_engine_name",
                        "workflow_engine_parameters", "workflow_url", "workflow_name", "workflow_attachment"]
        run_request: Dict[str, str] = {}
        for key in request_keys:
            if key in sapporo_run:
                run_request[key] = sapporo_run[key]

        return run_request

    @classmethod
    def execute_wf(cls, run_request: Dict[str, str], endpoint: str) -> str:
        data = urlencode(run_request).encode("utf-8")  # type: ignore
        # remove trailing slash from endpoint
        request = Request(f"{endpoint.rstrip('/')}/runs", data=data)  # type: ignore

        with urlopen(request) as response:
            result = json.load(response)
        if "run_id" not in result:
            raise ValueError(result)

        return result["run_id"]  # type: ignore

    @classmethod
    def get_run_status(cls, endpoint: str, run_id: str) -> str:
        request = Request(f"{endpoint.rstrip('/')}/runs/{run_id}/status")

        with urlopen(request) as response:
            result = json.load(response)
        if "state" not in result:
            raise ValueError(result)

        return result["state"]  # type: ignore

    @classmethod
    def sleep(cls, iter_num: int) -> None:
        """\
        Up to 1 minute, every 10 seconds: 10 * 6
        Up to 5 minutes, every 30 seconds: 10 * 6 + 30 * 8
        Up to 60 minutes, every 1 minute: 10 * 6 + 30 * 8 + 60 * 55
        Beyond that, every 2 minutes
        """
        if iter_num < 6:
            time.sleep(10)
        elif iter_num < 15:
            time.sleep(30)
        elif iter_num < 69:
            time.sleep(60)
        else:
            time.sleep(120)

    @classmethod
    def get_run_log(cls, endpoint: str, run_id: str) -> Dict[str, Any]:
        request = Request(f"{endpoint.rstrip('/')}/runs/{run_id}")

        with urlopen(request) as response:
            result = json.load(response)

        return result  # type: ignore

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        endpoint = self["sapporo_location"]
        run_request = self.generate_run_request_json(self)
        try:
            run_id = self.execute_wf(run_request, endpoint)
        except Exception as err:
            error.add("sapporo_location", f"Failed to execute workflow: {err}.")
            raise error from None

        status = self.get_run_status(endpoint, run_id)
        iter_num = 0

        while status in self.RUNNING:
            self.sleep(iter_num)
            status = self.get_run_status(endpoint, run_id)
            flask_log.debug(f"Status of sapporo run {run_id} is {status}.")
            iter_num += 1

        prev_status = self["state"]
        if status != prev_status:
            error.add("state", f"""\
                      The status of the workflow execution MUST be {prev_status}; got {status} instead.
                      Please check the log of the workflow execution using GET {endpoint.rstrip('/')}/runs/{run_id}.""")
            raise error

        if isinstance(self["outputs"], dict):
            outputs = crate.get_by_id_and_type(self["outputs"]["@id"], Dataset)
            if len(outputs) > 0:
                self["outputs"] = outputs[0]
            else:
                error.add("outputs", f"Dataset entity with @id {self['outputs']['@id']} is required in this crate, but not found.")
                raise error
        outputs_entities: List[Entity] = []
        for ent in self["outputs"]["hasPart"]:
            if isinstance(ent, dict):
                file = crate.get_by_id_and_type(ent["@id"], File)
                if len(file) > 0:
                    outputs_entities.append(file[0])
                else:
                    error.add("outputs", f"File entity with @id {ent['@id']} is required in this crate, but not found.")
                    raise error
            elif isinstance(ent, File):
                outputs_entities.append(ent)

        run_log = self.get_run_log(endpoint, run_id)
        file_names = [output["file_name"] for output in run_log["outputs"]]
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            for file_name in file_names:
                file_path = tmp_dir_path.joinpath(file_name)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with urlopen(f"{endpoint.rstrip('/')}/runs/{run_id}/data/outputs/{file_name}") as response:
                    with open(file_path, "wb") as f:
                        f.write(response.read())
                prev_file_entities = [ent for ent in outputs_entities if file_name == ent["name"]]
                if len(prev_file_entities) == 0:
                    error.add(
                        "outputs", f"The file {file_name} is included in the result of re-execution, but this crate does not have File entity with @id {file_name}.")
                    raise error
                prev_file_ent = prev_file_entities[0]

                if "contentSize" in prev_file_ent:
                    content_size = f"{file_path.stat().st_size}B"
                    if content_size != prev_file_ent["contentSize"]:
                        error.add("outputs", "The file size of {file_name}, {content_size}, does not match the `contentSize` value in {prev_file_ent}.")
                if "sha256" in prev_file_ent:
                    sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest()
                    if sha256 != prev_file_ent["sha256"]:
                        error.add("outputs", "The hash of {file_name} does not match the `sha256` value in {prev_file_ent}.")

        if error.has_error():
            raise error
