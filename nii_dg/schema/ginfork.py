#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity
from nii_dg.error import GovernanceError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import (check_all_prop_types, check_content_formats,
                          check_content_size, check_isodate, check_mime_type,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, classify_uri,
                          load_entity_def_from_schema_file,
                          verify_is_past_date)


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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

    def validate(self) -> None:
        pass

    def validate_multi_entities(self, rocrate: ROCrate) -> None:
        # TODO: impl.
        monitor_file_size(rocrate, self["contentSize"])


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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        if classify_uri(self, "@id") == "abs_path":
            raise PropsError(f"The value of @id property of {self} MUST be URL or relative path to the file, not absolute path.")

        check_content_formats(self, {
            "contentSize": check_content_size,
            "encodingFormat": check_mime_type,
            "url": check_url,
            "sha256": check_sha256,
            "sdDatePublished": check_isodate
        })

        if not verify_is_past_date(self, "sdDatePublished"):
            raise PropsError(f"The value of sdDatePublished property of {self} MUST be the date of past.")
        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

    def validate(self) -> None:
        # TODO: impl.
        pass


def monitor_file_size(rocrate: ROCrate, size: str) -> None:
    """
    File size sum が規定値を超えていないことを確認
    """
    # TODO: impl.
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit = units.index(size[-2:])
    limit = int(size[:-2])

    file_size_sum: float = 0
    for e in rocrate.get_by_entity_type(File):
        if e["contentSize"][-2:] in units:
            file_unit = units.index(e["contentSize"][-2:])
            file_size = int(e["contentSize"][:-2])
        else:
            file_unit = 0
            file_size = int(e["contentSize"][:-1])

        file_size_sum += round(file_size / 1024 ** (unit - file_unit), 3)

    if file_size_sum > limit:
        raise GovernanceError("The total file size of monitored ginfork file is larger than the defined size.")
