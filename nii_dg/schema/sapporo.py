#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity, DataEntity
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import File as BaseFile

SCHEMA_NAME = Path(__file__).stem


class File(BaseFile):
    def __init__(self, id_: str, props: Optional[Dict[str, Any]] = None):
        super(BaseFile, self).__init__(id_=id_, props=props, schema_name=SCHEMA_NAME)

    def check_props(self) -> None:
        pass

    def validate(self, crate: ROCrate) -> None:
        pass


class SapporoRun(ContextualEntity):
    def __init__(self, id_: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id_=id_, props=props, schema_name=SCHEMA_NAME)

    def check_props(self) -> None:
        pass

    def validate(self, crate: ROCrate) -> None:
        pass
