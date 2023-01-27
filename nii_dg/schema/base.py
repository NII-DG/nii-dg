#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from nii_dg.entity import ContextualEntity, DataEntity, DefaultEntity
from nii_dg.error import EntityError, PropsError, UnexpectedImplementationError
from nii_dg.utils import (EntityDef, access_url, check_all_prop_types,
                          check_content_formats, check_content_size,
                          check_email, check_isodate, check_mime_type,
                          check_orcid_id, check_phonenumber,
                          check_required_props, check_sha256,
                          check_unexpected_props, check_url, classify_uri,
                          get_name_from_ror, github_branch, github_repo,
                          load_entity_def_from_schema_file,
                          verify_is_past_date)

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


class RootDataEntity(DefaultEntity):
    """\
    See https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity.
    """

    def __init__(self, props: Optional[Dict[str, Any]] = None):
        super().__init__(id="./", props=props)
        self["@type"] = "Dataset"

    def __init_subclass__(cls) -> None:
        raise UnexpectedImplementationError("Inheritance of RootDataEntity is not allowed.")

    @property
    def context(self) -> str:
        """/
        Special context for RootDataEntity.
        """
        template = "https://raw.githubusercontent.com/{repo}/{branch}/schema/context/{schema}/{entity}.json"
        return template.format(
            repo=github_repo(),
            branch=github_branch(),
            schema=self.schema_name,
            entity="RootDataEntity",
        )

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
        entity_def_of_root: EntityDef = {prop: obj for prop, obj in entity_def.items() if prop not in ["dateCreated", "hasPart"]}  # type: ignore

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def_of_root)
        check_all_prop_types(self, entity_def)

        if self.id != "./":
            raise PropsError("The value of @id property of RootDataEntity MUST be './'.")

        if self.type != "Dataset":
            raise PropsError("The value of @type property of RootDataEntity MUST be 'Dataset'.")

    def validate(self, crate: "ROCrate") -> None:
        pass


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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        if classify_uri(self, "@id") == "abs_path":
            raise PropsError(f"The @id value of {self} MUST be URL or relative path to the file, not absolute path.")

        check_content_formats(self, {
            "contentSize": check_content_size,
            "url": check_url,
            "sha256": check_sha256,
            "encodingFormat": check_mime_type,
            "sdDatePublished": check_isodate
        })

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

        if verify_is_past_date(self, "sdDatePublished") is False:
            raise PropsError(f"The value of sdDatePublished property of {self} MUST be the date of past.")

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        if classify_uri(self, "@id") == "URL":
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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "url": check_url
        })

        if not self.id.endswith("/"):
            raise PropsError(f"The value of @id property of {self} MUST end with '/'.")

        if classify_uri(self, "@id") != "rel_path":
            raise PropsError(f"The value of @id property of {self} MUST be relative path to the directory, neither absolute path nor URL.")

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url,
            "url": check_url
        })

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        if self.id.startswith("https://ror.org/"):
            ror_namelist = get_name_from_ror(self.id[16:])
            if self["name"] not in ror_namelist:
                validation_failures.add("name", f"The value MUST be same as the registered name in ROR. See {self.id}.")
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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url,
            "email": check_email,
            "telephone": check_phonenumber
        })

        if self.id.startswith("https://orcid.org/"):
            check_orcid_id(self.id[18:])

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url
        })

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        classify_uri(self, "@id")

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url,
            "sha256": check_sha256,
            "uploadDate": check_isodate
        })

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

        if verify_is_past_date(self, "uploadDate") is False:
            raise PropsError(f"The value of uploadDate property of {self} MUST be the date of past.")

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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "@id": check_url,
            "url": check_url
        })

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        if self.id.startswith("https://ror.org/"):
            ror_namelist = get_name_from_ror(self.id[16:])
            if self["name"] not in ror_namelist:
                validation_failures.add("name", f"The value MUST be same as the registered name in ROR. See {self.id}.")
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
        entity_def = load_entity_def_from_schema_file(self.schema_name, self.entity_name)

        check_unexpected_props(self, entity_def)
        check_required_props(self, entity_def)
        check_all_prop_types(self, entity_def)

        check_content_formats(self, {
            "email": check_email,
            "telephone": check_phonenumber
        })

        if self.type != self.entity_name:
            raise PropsError(f"The value of @type property of {self} MUST be '{self.entity_name}'.")

        if self.id[:8] not in ["#mailto:", "#callto:"]:
            raise PropsError(f"The value of @id property of {self} MUST be start with #mailto: or #callto:.")

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
