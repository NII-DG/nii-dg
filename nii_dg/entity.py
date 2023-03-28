#!/usr/bin/env python3
# coding: utf-8

from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Dict, Type

import yaml

from nii_dg.const import RO_CRATE_SPEC
from nii_dg.error import EntityError
from nii_dg.utils import (NOW, EntityDef, generate_ctx,
                          is_instance_of_expected_type)

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate
    TypedMutableMapping = MutableMapping[str, Any]
else:
    TypedMutableMapping = MutableMapping


class Entity(TypedMutableMapping):
    data: Dict[str, Any]
    schema_name: str
    entity_def: EntityDef

    def __init__(self, id_: str, props: Dict[str, Any], schema_name: str, entity_def: EntityDef) -> None:
        self.data = {
            "@id": id_,
            "@type": self.entity_name,
            "@context": generate_ctx(schema_name=schema_name),
        }
        self.schema_name = schema_name
        self.entity_def = entity_def

        # If props include keys starting with '@', raise an error.
        # Use _set_special_item() instead for these special keys in subclasses.
        self.update(props)

    def __setitem__(self, key: str, value: Any) -> None:
        if key.startswith("@"):
            raise KeyError("The key must not start with '@'.")
        self.data[key] = value

    def _set_special_item(self, key: str, value: Any) -> None:
        """\
        Set a special item, which key starts with '@' (e.g. "@id", "@type", "@context").
        """
        self.data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __delitem__(self, key: str) -> None:
        if key.startswith("@"):
            raise KeyError("The key must not start with '@'.")
        del self.data[key]

    def __iter__(self) -> Any:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        if isinstance(self, DefaultEntity):
            return f"<{self.type} {self.id}>"

        return f"<{self.schema_name}.{self.type} {self.id}>"

    @property
    def id(self) -> str:
        return self["@id"]  # type: ignore

    @property
    def type(self) -> str:
        return self["@type"]  # type: ignore

    @property
    def context(self) -> str:
        return self["@context"]  # type: ignore

    @property
    def entity_name(self) -> str:
        return self.__class__.__name__

    @classmethod
    def from_jsonld(cls: Type["Entity"], jsonld: Dict[str, Any]) -> "Entity":
        """\
        Create an instance of the subclass of Entity from a JSON-LD object.

        Args:
            cls: The subclass of Entity to create.
            jsonld (Dict[str, Any]): A JSON-LD object.
        """
        if cls.__name__ == "Entity":
            raise NotImplementedError("This method is not implemented for Entity class, but for its subclasses.")

        if not isinstance(jsonld, dict):
            raise ValueError("The JSON-LD object must be a dictionary.")
        if "@id" not in jsonld:
            raise ValueError("The JSON-LD object must have an @id property.")

        props = {k: v for k, v in jsonld.items() if not k.startswith("@")}
        special_props = {k: v for k, v in jsonld.items() if k.startswith("@")}
        entity = cls(id_=jsonld["@id"], props=props)  # type: ignore
        for key, val in special_props.items():
            entity._set_special_item(key, val)

        return entity

    def as_jsonld(self) -> Dict[str, Any]:
        ref_data: Dict[str, Any] = {}
        for key, val in self.items():
            if isinstance(val, dict):
                # expect: {"@id": "xxx"}, {"@value": "xxx"}
                ref_data[key] = val
            elif isinstance(val, list):
                # expect: [Any, Entity, ...]
                ref_val = []
                for v in val:
                    if isinstance(v, Entity):
                        ref_val.append({"@id": v.id})
                    else:
                        ref_val.append(v)
                ref_data[key] = ref_val
            elif isinstance(val, Entity):
                ref_data[key] = {"@id": val.id}
            else:
                ref_data[key] = val

        return ref_data

    def _check_unexpected_props(self) -> None:
        entity_error = EntityError(self)
        for key in self.keys():
            if key.startswith("@"):
                continue
            if key not in self.entity_def["props"]:
                entity_error.add(key, "Unexpected property.")

        if entity_error.has_error():
            raise entity_error

    def _check_required_props(self) -> None:
        entity_error = EntityError(self)
        required_keys = [k for k, v in self.entity_def["props"].items() if v.get("required") == "Required."]
        for key in required_keys:
            if key not in self:
                entity_error.add(key, "This property is required; however, it is not found.")

        if entity_error.has_error():
            raise entity_error

    def _check_prop_types(self) -> None:
        entity_error = EntityError(self)
        for key, val in self.items():
            if key.startswith("@"):
                continue
            if key not in self.entity_def["props"]:
                continue
            expected_type = self.entity_def["props"][key]["expected_type"]
            if not is_instance_of_expected_type(val, expected_type):
                entity_error.add(key, f"The type of this property MUST be {expected_type}.")

        if entity_error.has_error():
            raise entity_error

    def check_props(self) -> None:
        if self.entity_name == "Entity":
            raise NotImplementedError("This method must be implemented in subclasses of Entity in schema modules.")

        self._check_unexpected_props()
        self._check_required_props()
        self._check_prop_types()

    def validate(self, crate: "ROCrate") -> None:
        if self.entity_name == "Entity":
            raise NotImplementedError("This method must be implemented in subclasses of Entity in schema modules.")


class DefaultEntity(Entity):
    pass


class DataEntity(Entity):
    pass


class ContextualEntity(Entity):
    pass


# === DefaultEntities ===

RootDataEntity_DEF: EntityDef = yaml.safe_load("""\
description: A Dataset that represents the RO-Crate.
props:
  hasPart:
    expected_type: List[DataEntity]
    example: '[{ "@id": "file.txt" }]'
    required: Required.
    description: A list of DataEntities that are contained in the RO-Crate.
  datePublished:
    expected_type: str
    example: 2023-01-01T00:00:00.000+00:00
    required: Required.
    description: The date when the RO-Crate was published. It should be in the format of ISO 8601.
""")


class RootDataEntity(DefaultEntity):
    def __init__(self, props: Dict[str, Any] = {},
                 schema_name: str = "ro-crate",
                 entity_def: EntityDef = RootDataEntity_DEF):
        default_props = {
            "hasPart": [],
            "datePublished": NOW
        }
        default_props.update(props)
        super().__init__(id_="./", props=default_props, schema_name=schema_name, entity_def=entity_def)

        self._set_special_item("@type", "Dataset")

    def check_props(self) -> None:
        # do nothing
        pass

    def validate(self, crate: "ROCrate") -> None:
        # do nothing
        pass


ROCrateMetadata_DEF: EntityDef = yaml.safe_load("""\
description: The RO-Crate metadata file descriptor.
props:
  conformsTo:
    expected_type: Dict[str, str]
    example: '{ "@id": "https://w3id.org/ro/crate/1.1" }'
    required: Required.
    description: A versioned permanent link URI of the RO-Crate specification
  about:
    expected_type: RootDataEntity
    example: '{ "@id": "./" }'
    required: Required.
    description: The RootDataEntity of the RO-Crate.
""")


class ROCrateMetadata(DefaultEntity):
    def __init__(self, props: Dict[str, Any] = {},
                 schema_name: str = "ro-crate",
                 entity_def: EntityDef = ROCrateMetadata_DEF):
        default_props = {
            "conformsTo": {"@id": RO_CRATE_SPEC},
            "about": {"@id": "./"},
        }
        default_props.update(props)
        super().__init__(id_="ro-crate-metadata.json", props=default_props, schema_name=schema_name, entity_def=entity_def)

        self._set_special_item("@type", "CreativeWork")

    def check_props(self) -> None:
        # do nothing
        pass

    def validate(self, crate: "ROCrate") -> None:
        # do nothing
        pass
