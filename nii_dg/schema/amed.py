#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import Any, Dict, Optional

from nii_dg.entity import ContextualEntity
from nii_dg.error import GovernanceError, PropsError
from nii_dg.schema.base import File as BaseFile
from nii_dg.utils import (access_url, check_all_prop_types,
                          check_content_formats, check_content_size,
                          check_isodate, check_mime_type, check_required_props,
                          check_sha256, check_unexpected_props, check_url,
                          classify_uri, load_entity_def_from_schema_file,
                          verify_is_past_date)


class DMPMetadata(ContextualEntity):
    def __init__(self, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="#AMED-DMP", props=props)
        self["name"] = "AMED-DMP"

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
        """\
        memo:
        - 欲している (required) prop があるか -> check required
        - optional prop -> あればチェック type
        - 全然知らんやつ prop -> 例外
        """
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)
        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        if self["@id"] != "#AMED-DMP":
            raise PropsError("The value of @id property of DMPMetadata entity in AMED MUST be '#AMED-DMP'.")
        if self["name"] != "AMED-DMP":
            raise PropsError("The value of name property of DMPMetadata entity in AMED MUST be 'AMED-DMP'.")

    def validate(self) -> None:
        # TODO: impl.
        pass


class DMP(ContextualEntity):
    def __init__(self, id: int, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="#dmp:" + str(id), props=props)

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

        check_content_formats(self, {
            "availabilityStarts": check_isodate
        })

        if verify_is_past_date(self, "availabilityStarts"):
            raise PropsError("The value of availabilityStarts MUST be the date of future.")

    def validate(self) -> None:

        if self["accessRights"] in ["Unshared", "Restricted Closed Sharing"]:
            if any(map(self.keys().__contains__, ("availabilityStarts", "accessRightsInfo"))) is False:
                raise GovernanceError(
                    f"The property availabilityStarts is required in {self}. If you keep data unshared, property AccessRightsInfo is required instead.")

        if "repository" not in self.keys():
            # TODO: DMPMetadataエンティティを見に行く,なければGovernanceError
            pass
        if self["accessRights"] == "Unrestricted Open Sharing" and "distribution" not in self.keys():
            # TODO: DMPMetadataエンティティを見に行く,なければGovernanceError
            pass

        if self["gotInformedConsent"] == "yes" and "informedConsentFormat" not in self.keys():
            raise GovernanceError(f"The property informedConsentFormat is required in {self}.")


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
            raise PropsError(f"The @id value in {self} MUST be URL or relative path to the file, not absolute path.")

        check_content_formats(self, {
            "contentSize": check_content_size,
            "encodingFormat": check_mime_type,
            "url": check_url,
            "sha256": check_sha256,
            "sdDatePublished": check_isodate
        })

        if verify_is_past_date(self, "sdDatePublished") is False:
            raise PropsError("The value of sdDatePublished MUST not be the date of future.")

    def validate(self) -> None:
        # TODO: impl.
        if classify_uri(self, "@id") == "url":
            if "sdDatePublished" not in self.keys():
                raise GovernanceError(f"The property sdDatePublished MUST be included in {self}.")


class ClinicalResearchRegistration(ContextualEntity):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

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

        check_content_formats(self, {
            "@id": check_url,
        })

    def validate(self) -> None:
        access_url(self["@id"])
