#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from nii_dg.entity import ContextualEntity, DataEntity
from nii_dg.error import EntityError, PropsError
from nii_dg.utils import (access_url, check_all_prop_types,
                          check_content_formats, check_content_size,
                          check_email, check_isodate, check_mime_type,
                          check_orcid_id, check_phonenumber,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, classify_uri,
                          get_name_from_ror, load_entity_def_from_schema_file,
                          verify_is_past_date)

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


class File(DataEntity):
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
                "url": check_url,
                "sha256": check_sha256,
                "encodingFormat": check_mime_type,
                "sdDatePublished": check_isodate
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        try:
            if verify_is_past_date(self, "sdDatePublished") is False:
                prop_errors.add("sdDatePublished", "The value MUST be the date of past.")
        except (TypeError, ValueError):
            prop_errors.add("sdDatePublished", "The value is invalid date format. MUST be 'YYYY-MM-DD'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        if classify_uri(self.id) == "URL":
            if "sdDatePublished" not in self.keys():
                validation_failures.add("sdDatepublished", "This property is required, but not found.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class Dataset(DataEntity):
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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            check_content_formats(self, {
                "url": check_url
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if not self.id.endswith("/"):
            prop_errors.add("@id", "The value MUST end with '/'.")

        try:
            if classify_uri(self.id) != "rel_path":
                prop_errors.add("@id", "The value MUST be relative path to the directory, neither absolute path nor URL.")
        except ValueError as error:
            prop_errors.add("@id", str(error))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        pass


class Organization(ContextualEntity):
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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            check_content_formats(self, {
                "@id": check_url,
                "url": check_url
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        if self.id.startswith("https://ror.org/"):
            try:
                ror_namelist = get_name_from_ror(self.id[16:])
                if self["name"] not in ror_namelist:
                    validation_failures.add("name", f"The value MUST be same as the registered name in ROR. See {self.id}.")
            except ValueError as e:
                validation_failures.add("@id", str(e))
        else:
            try:
                access_url(self.id)
            except ValueError as e:
                validation_failures.add("@id", str(e))

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class Person(ContextualEntity):
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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            check_content_formats(self, {
                "@id": check_url,
                "email": check_email,
                "telephone": check_phonenumber
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        try:
            if type(self.id) is str and self.id.startswith("https://orcid.org/"):
                check_orcid_id(self.id[18:])
        except ValueError as e:
            prop_errors.add("@id", str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        try:
            access_url(self.id)
        except ValueError as e:
            validation_failures.add("@id", str(e))

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class License(ContextualEntity):
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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            check_content_formats(self, {
                "@id": check_url
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        try:
            access_url(self.id)
        except ValueError as e:
            validation_failures.add("@id", str(e))

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class RepositoryObject(ContextualEntity):
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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            classify_uri(self.id)
        except ValueError as error:
            prop_errors.add("@id", str(error))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        pass


class DataDownload(ContextualEntity):
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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            check_content_formats(self, {
                "@id": check_url,
                "sha256": check_sha256,
                "uploadDate": check_isodate
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        try:
            if verify_is_past_date(self, "uploadDate") is False:
                prop_errors.add("uploadDate", "The value MUST be the date of past.")
        except (TypeError, ValueError):
            prop_errors.add("uploadDate", "The value is invalid date format. MUST be 'YYYY-MM-DD'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        try:
            access_url(self.id)
        except ValueError as e:
            validation_failures.add("@id", str(e))

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class HostingInstitution(Organization):
    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id=id, props=props)

    @property
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

        try:
            check_content_formats(self, {
                "@id": check_url,
                "url": check_url
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        if self.id.startswith("https://ror.org/"):
            try:
                ror_namelist = get_name_from_ror(self.id[16:])
                if self["name"] not in ror_namelist:
                    validation_failures.add("name", f"The value MUST be same as the registered name in ROR. See {self.id}.")
            except ValueError as e:
                validation_failures.add("@id", str(e))
        else:
            try:
                access_url(self.id)
            except ValueError as e:
                validation_failures.add("@id", str(e))

        if len(validation_failures.message_dict) > 0:
            raise validation_failures


class ContactPoint(ContextualEntity):
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
        prop_errors = EntityError(self)
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        for func in [check_unexpected_props, check_required_props, check_all_prop_types]:
            try:
                func(self, entity_def)
            except PropsError as e:
                prop_errors.add_by_dict(str(e))

        try:
            check_content_formats(self, {
                "email": check_email,
                "telephone": check_phonenumber
            })
        except PropsError as e:
            prop_errors.add_by_dict(str(e))

        if self.type != self.entity_name:
            prop_errors.add("@type", f"The value MUST be '{self.entity_name}'.")

        if self.id[:8] not in ["#mailto:", "#callto:"]:
            prop_errors.add("@id", "The value MUST be start with #mailto: or #callto:.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        if self.id.startswith("#mailto:"):
            if "email" not in self.keys():
                validation_failures.add("email", "This property is required, but not found.")
            elif self.id[8:] != self["email"]:
                validation_failures.add("@id", "The contained email is not the same as the value of email property.")
                validation_failures.add("email", "The value is not the same as the email contained in the value of @id property.")

        elif self.id.startswith("#callto:"):
            if "telephone" not in self.keys():
                validation_failures.add("telephone", "This property is required, but not found.")
            elif self.id[8:] != self["telephone"] or self.id[8:] != self["telephone"].replace("-", ""):
                validation_failures.add("@id", "The contained phone number is not the same as the value of telephone property.")
                validation_failures.add("telephone", "The value is not the same as the phone number contained in the value of @id property.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures
