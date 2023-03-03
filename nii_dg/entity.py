#!/usr/bin/env python3
# coding: utf-8

"""\
Definition of Entity base class and its subclasses.
"""

from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Dict, Optional, TypedDict

from typeguard import check_type as ori_check_type

from nii_dg.config import github_branch, github_repo
from nii_dg.error import EntityError, PropsError
from nii_dg.utils import (check_instance_type_from_id, check_prop_type,
                          get_entity_list_to_validate)

if TYPE_CHECKING:
    TypedMutableMapping = MutableMapping[str, Any]
    from nii_dg.ro_crate import ROCrate
else:
    TypedMutableMapping = MutableMapping

IdDict = TypedDict("IdDict", {"@id": str})


class Entity(TypedMutableMapping):
    """\
    Base class for all entities.

    By inheriting MutableMapping, this class implements the following methods:
    `__contains__`, `__eq__`, `__ne__`, `get`, `pop`, `popitem`, `setdefault`, `update`, `clear`, `keys`, `values` and `items`.
    """

    def __init__(self, id_: str, props: Optional[Dict[str, Any]] = None, schema_name: Optional[str] = None) -> None:
        if props and [key for key in props.keys() if key.startswith("@")] != []:
            raise KeyError("Cannot set the property started with @.")

        self.__schema_name = schema_name
        self.data: Dict[str, Any] = {
            "@id": id_,
            "@type": self.entity_name,
            "@context": self.context
        }
        self.update(props or {})

    def __setitem__(self, key: str, value: Any) -> None:
        if key.startswith("@") and key != "@id":
            raise KeyError(f"Cannot set {key} as property; property with @ is limited.")
        self.data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __delitem__(self, key: str) -> None:
        if key.startswith("@"):
            raise KeyError(f"Cannot delete protected key: {key}")
        del self.data[key]

    def __iter__(self) -> Any:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        if isinstance(self, DefaultEntity):
            return f"<{self.type} {self.id}>"

        return f"<{self.schema_name}.{self.type} {self.id}>"

    # def __eq__(self) -> str:
    #     # TODO
    #     return self.id + self.context

    @property
    def id(self) -> str:
        return self.data["@id"]  # type:ignore

    @property
    def type(self) -> str:
        return self.data["@type"]  # type:ignore

    @property
    def context(self) -> str:
        template = "https://raw.githubusercontent.com/{gh_repo}/{gh_ref}/schema/context/{schema}.jsonld"
        return template.format(
            gh_repo=github_repo(),
            gh_ref=github_branch(),
            schema=self.schema_name,
        )

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    @property
    def schema_name(self) -> Optional[str]:
        """\
        This property is not set for DefaultEntity.
        """
        return self.__schema_name

    def as_jsonld(self) -> Dict[str, Any]:
        """\
        Dump this entity as JSON-LD.
        Basically, it is assumed that self.check_props method checks the existence of required props and the type of props.
        In addition, this method replace entities in props with their id.
        """
        self.check_props()
        ref_data: Dict[str, Any] = {}
        for key, val in self.items():
            if isinstance(val, dict):
                # expected: {"@id": str}, {"@value": Any}
                # These cannot be supported at this stage, should be supported in self.check_props.
                ref_data[key] = val
            elif isinstance(val, list):
                # expected: [Any], [Entity], [Entity, Any]
                fixed_val = []
                id_set = set()
                for v in val:
                    if isinstance(v, Entity):
                        if v.id not in id_set:
                            fixed_val.append({"@id": v.id})
                            id_set.add(v.id)
                    else:  # case: Any (not Entity)
                        fixed_val.append(v)
                ref_data[key] = fixed_val
            elif isinstance(val, Entity):
                ref_data[key] = {"@id": val.id}
            else:
                ref_data[key] = val
        return ref_data

    def check_props(self) -> None:
        """\
        Called at RO-Crate dump time.
        Check if all required props are set and if prop types are correct.
        Implementation of this method is required in each subclass.
        """
        # Abstract method
        raise NotImplementedError

    def validate(self, crate: "ROCrate") -> None:
        """\
        Called at Data Governance validation time.
        Comprehensive validation including the value of props.
        Implementation of this method is required in each subclass.
        """
        # Abstract method
        # raise NotImplementedError
        validation_failures = EntityError(self)
        instance_type_dict = get_entity_list_to_validate(self)

        for prop, val in self.items():
            if isinstance(val, Entity):
                if val not in crate.get_all_entities():
                    validation_failures.add(prop, f"The entity {val} is not included in the crate.")
                if prop in instance_type_dict:
                    try:
                        check_prop_type(prop, val, instance_type_dict[prop])
                    except PropsError as e:
                        validation_failures.add(prop, str(e))

            elif isinstance(val, dict) and prop in instance_type_dict:
                # expected: {"@id":"https://example.com"}
                try:
                    ori_check_type(prop, val, IdDict)
                except TypeError:
                    validation_failures.add(prop, "Only property @id is required when using dict instead of entity subclass instance.")
                if "@id" in val and len(crate.get_by_id(val["@id"])) == 0:
                    validation_failures.add(prop, f"Entity with @id {val['@id']} is not found in the crate.")

                if "@id" in val and prop in instance_type_dict:
                    try:
                        check_instance_type_from_id(prop, crate.get_by_id(val["@id"]), instance_type_dict[prop])
                    except PropsError as e:
                        validation_failures.add(prop, str(e))

            elif isinstance(val, list):
                # expected: [Any], [Entity]
                for ele in [v for v in val if isinstance(v, Entity)]:
                    if ele not in crate.get_all_entities():
                        validation_failures.add(prop, f"The entity {ele} is not included in this crate.")
                    if prop in instance_type_dict:
                        try:
                            check_prop_type(prop, [ele], instance_type_dict[prop])
                        except PropsError as e:
                            validation_failures.add(prop, str(e))

                for id_dict in [v for v in val if isinstance(v, dict)]:
                    try:
                        ori_check_type(prop, id_dict, IdDict)
                    except TypeError:
                        validation_failures.add(prop, "Only property @id is required when using dict instead of entity subclass instance.")
                    if "@id" in id_dict and len(crate.get_by_id(id_dict["@id"])) == 0:
                        validation_failures.add(prop, f"Entity with @id {id_dict['@id']} is not found in the crate.")
                    if "@id" in id_dict and prop in instance_type_dict:
                        try:
                            check_instance_type_from_id(prop, crate.get_by_id(id_dict["@id"]), instance_type_dict[prop], "list")
                        except PropsError as e:
                            validation_failures.add(prop, str(e))
            else:
                if prop in instance_type_dict:
                    try:
                        check_prop_type(prop, val, instance_type_dict[prop])
                    except PropsError as e:
                        validation_failures.add(prop, str(e))

        if len(validation_failures.message_dict) > 0:
            raise validation_failures

    @classmethod
    def from_jsonld(cls, id_: str, jsonld: Dict[str, Any]) -> "Entity":
        """\
        Generate entity instance from json-ld.
        This method is called in from_jsonld() of ROCrate.
        """
        # if "@id" not in jsonld:
        #     raise ValueError(f"Entity must have @id: {jsonld}")
        # id_ = jsonld["@id"]
        props = {k: v for k, v in jsonld.items() if not k.startswith("@")}
        return cls(id_, props)


class DefaultEntity(Entity):
    """\
    A entity that is always included in the RO-Crate. For example, ROCrateMetadata, RootDataEntity, etc.
    """

    def __init__(self, id_: str, props: Optional[Dict[str, Any]] = None, type_: Optional[str] = None) -> None:
        if props and [key for key in props.keys() if key.startswith("@")] != []:
            raise KeyError("Cannot set the property started with @.")

        # DefaultEntity uses the defined type as @type, not the entity name.
        # DefaultEntity uses the original RO-Crate context, so the @context property is not included.
        self.data: Dict[str, Any] = {
            "@id": id_,
            "@type": type_
        }
        self.update(props or {})

    @property
    def context(self) -> str:
        # DefaultEntity uses the original RO-Crate context.
        return "https://w3id.org/ro/crate/1.1/context"


class DataEntity(Entity):
    """\
    A entity that represents a file or directory. For example, File, Dataset, etc.
    This entity is always included in RootDataset entity.
    """


class ContextualEntity(Entity):
    """\
    A entity that represents a metadata. For example, Person, License, etc.
    """


class RootDataEntity(DefaultEntity):
    """\
    A Dataset that represents the RO-Crate. For more information, see https://www.researchobject.org/ro-crate/1.1/root-data-entity.html .
    """

    def __init__(self, props: Optional[Dict[str, Any]] = None):
        super().__init__(id_="./", props=props, type_="Dataset")
        # `hasPart` and `datePublished` are added in `RO-Crate` class.

    def check_props(self) -> None:
        prop_errors = EntityError(self)

        if self.id != "./":
            prop_errors.add("@id", "The value MUST be `./`.")

        if self.type != "Dataset":
            prop_errors.add("@type", "The value MUST be `Dataset`.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        # TODO: link check
        pass


class ROCrateMetadata(DefaultEntity):
    """\
    RO-Crate must contain a RO-Crate metadata file descriptor with the `@id` of `ro-crate-metadata.json`.

    See https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#ro-crate-metadata-file-descriptor.
    """

    def __init__(self, root: RootDataEntity) -> None:
        super().__init__(id_="ro-crate-metadata.json", type_="CreativeWork")
        self["conformsTo"] = {"@id": "https://w3id.org/ro/crate/1.1"}
        self["about"] = root

    def check_props(self) -> None:
        prop_errors = EntityError(self)

        if self.id != "ro-crate-metadata.json":
            prop_errors.add("@id", "The value MUST be `ro-crate-metadata.json`.")

        if "conformsTo" not in self:
            prop_errors.add("conformsTo", "This property is required and the value MUST be `{'@id': 'https: // w3id.org/ro/crate/1.1'}`.")

        if "conformsTo" in self and self["conformsTo"] != {"@id": "https://w3id.org/ro/crate/1.1"}:
            prop_errors.add("conformsTo", "The value MUST be `{'@id': 'https: // w3id.org/ro/crate/1.1'}`.")

        if self.type != "CreativeWork":
            prop_errors.add("@type", "The value MUST be `CreativeWork`.")

        if len(prop_errors.message_dict) > 0:
            raise prop_errors

    def validate(self, crate: "ROCrate") -> None:
        validation_failures = EntityError(self)

        if self["about"] != {"@id": "./"} and self["about"] != crate.root:
            validation_failures.add("about", "The value of about property MUST be RootDataEntity of the crate.")

        if len(validation_failures.message_dict) > 0:
            raise validation_failures
