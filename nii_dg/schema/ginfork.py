#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity, DataEntity
from nii_dg.error import PropsError
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import (check_allprops_type, check_content_size,  # noqa
                          check_isodate, check_mime_type, check_required_props,
                          check_sha256, check_uri, load_entity_schema)


class GinMonitoring(ContextualEntity):
    def __init__(self, id: int, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="#ginmonitoring:" + str(id), props=props)

    @property
    def schema(self) -> str:
        return Path(__file__).stem

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_props()
        return super().as_jsonld()

    def check_props(self) -> None:
        schema = load_entity_schema(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_allprops_type(self, schema["type_dict"])

    def validate(self) -> None:
        # TODO: impl.
        pass


class File(BaseFile):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    def check_props(self) -> None:
        schema = load_entity_schema(self.schema, self.__class__.__name__)

        check_required_props(self, schema["required_list"])
        check_allprops_type(self, schema["type_dict"])

        if check_uri(self, "@id") == "abs_path":
            raise PropsError(f"The @id value in {self} MUST be URL or relative path to the file, not absolute path.")
        check_content_size(self, "contentSize")

        try:
            check_mime_type(self)
            check_sha256(self)
            check_uri(self, "url", "url")
            check_isodate(self, "sdDatePublished", "past")
        except KeyError:
            pass

    def validate(self) -> None:
        # TODO: impl.
        pass
