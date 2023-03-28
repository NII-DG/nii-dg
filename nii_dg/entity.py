#!/usr/bin/env python3
# coding: utf-8

"""\
Defines the Entity class and its subclasses used in the nii_dg package.
"""

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
    """\
    Represents an Entity that can be included in an RO-Crate.

    An Entity is a JSON-LD object that must have an "@id" property, an "@type" property, and an "@context" property.
    The properties and their expected types of an Entity are defined in its schema definition.
    """
    data: Dict[str, Any]
    schema_name: str
    entity_def: EntityDef

    def __init__(self, id_: str, props: Dict[str, Any], schema_name: str, entity_def: EntityDef) -> None:
        """\
        Initialize the Entity.

        Args:
            id_ (str): The ID of the Entity.
            props (Dict[str, Any]): The properties of the Entity.
            schema_name (str): The name of the schema that defines the Entity, e.g. "base".
            entity_def (EntityDef): The definition of the Entity.
        """
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
        """\
        Set the value of a property of the Entity.

        Args:
            key (str): The key of the property.
            value (Any): The value of the property.

        Raises:
            KeyError: If the key starts with "@".
        """
        if key.startswith("@"):
            raise KeyError("The key must not start with '@'.")
        self.data[key] = value

    def _set_special_item(self, key: str, value: Any) -> None:
        """\
        Set a special item, which key starts with '@' (e.g. "@id", "@type", "@context").

        Args:
            key (str): The key of the special item.
            value (Any): The value of the special item.
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
        """Return the ID of the Entity."""
        return self["@id"]  # type: ignore

    @property
    def type(self) -> str:
        """Return the type of the Entity."""
        return self["@type"]  # type: ignore

    @property
    def context(self) -> str:
        """Return the context of the Entity."""
        return self["@context"]  # type: ignore

    @property
    def entity_name(self) -> str:
        """Return the name of the Entity."""
        return self.__class__.__name__

    @classmethod
    def from_jsonld(cls: Type["Entity"], jsonld: Dict[str, Any]) -> "Entity":
        """\
        Create an instance of the subclass of Entity from a JSON-LD object.

        Args:
            cls: The subclass of Entity to create.
            jsonld (Dict[str, Any]): A JSON-LD object.

        Raises:
            NotImplementedError: If the method is called on the Entity class instead of its subclasses.
            ValueError: If the JSON-LD object is not a dictionary, or does not have an @id property.

        Returns:
            Entity: An instance of the subclass of Entity.
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
        """\
        Return the JSON-LD representation of the Entity.

        Returns:
            Dict[str, Any]: The JSON-LD representation of the Entity.
        """
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
        """\
        Check if there are unexpected properties in the Entity.

        Raises:
            EntityError: If there are unexpected properties.
        """
        entity_error = EntityError(self)
        for key in self.keys():
            if key.startswith("@"):
                continue
            if key not in self.entity_def["props"]:
                entity_error.add(key, "Unexpected property.")

        if entity_error.has_error():
            raise entity_error

    def _check_required_props(self) -> None:
        """\
        Check if all required properties are in the Entity.

        Raises:
            EntityError: If there are missing required properties.
        """
        entity_error = EntityError(self)
        required_keys = [k for k, v in self.entity_def["props"].items() if v.get("required") == "Required."]
        for key in required_keys:
            if key not in self:
                entity_error.add(key, "This property is required; however, it is not found.")

        if entity_error.has_error():
            raise entity_error

    def _check_prop_types(self) -> None:
        """\
        Check if all properties have the expected type.

        Raises:
            EntityError: If there are properties with unexpected types.
        """
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
        """\
        Called at Package validation time.
        Check if the properties of the Entity are valid.
        Implementation of this method is required in each subclass.

        Raises:
            EntityError: If there is an error in the Entity.
        """
        if self.entity_name == "Entity":
            raise NotImplementedError("This method must be implemented in subclasses of Entity in schema modules.")

        self._check_unexpected_props()
        self._check_required_props()
        self._check_prop_types()

    def validate(self, crate: "ROCrate") -> None:
        """\
        Called at Data Governance validation time.
        Comprehensive validation including the value of props.
        Implementation of this method is required in each subclass.

        Args:
            crate (ROCrate): The RO-Crate containing the Entity.

        Raises:
            EntityError: If there is an error in the Entity.
        """
        if self.entity_name == "Entity":
            raise NotImplementedError("This method must be implemented in subclasses of Entity in schema modules.")


class DefaultEntity(Entity):
    """\
    A entity that is always included in the RO-Crate. For example, ROCrateMetadata, RootDataEntity, etc.
    """


class DataEntity(Entity):
    """\
    A entity that represents a file or directory. For example, File, Dataset, etc.
    This entity is always included in RootDataset entity.
    """


class ContextualEntity(Entity):
    """\
    A entity that represents a metadata. For example, Person, License, etc.
    """


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
    """\
    A Dataset that represents the RO-Crate.

    For more information, see https://www.researchobject.org/ro-crate/1.1/root-data-entity.html .
    """

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
    """\
    The RO-Crate metadata file descriptor.

    See https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#ro-crate-metadata-file-descriptor.
    """

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
