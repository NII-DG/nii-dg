#!/usr/bin/env python3
# coding: utf-8

"""\
Definition of RO-Crate class.
"""

import json
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from urllib.parse import urlparse

from nii_dg.entity import (ContextualEntity, DataEntity, DefaultEntity, Entity,
                           ROCrateMetadata, RootDataEntity)
from nii_dg.error import (CheckPropsError, CrateError, EntityError,
                          GovernanceError, UnexpectedImplementationError)
from nii_dg.utils import import_entity_class


class ROCrate():
    """\
    RO-Crate class.
    This class has entities and metadata that represent a RO-Crate.
    In addition, this class provides methods for adding entities, dumping the RO-Crate, etc.

    As entities, all use classes that inherit from the Entity class.
    There are three types of entities: default, data, and contextual as follows:

    - Default entity: A entity that is always included in the RO-Crate. For example, ROCrateMetadata, RootDataEntity, etc.
    - Data entity: A entity that represents a file or directory. For example, File, Dataset, etc.
    - Contextual entity: A entity that represents a metadata. For example, Person, License, etc.

    For the details of RO-Crate, see https://www.researchobject.org/ro-crate/.
    """

    default_entities: List[DefaultEntity]
    data_entities: List[DataEntity]
    contextual_entities: List[ContextualEntity]

    root: RootDataEntity

    BASE_CONTEXT: str = "https://w3id.org/ro/crate/1.1/context"

    def __init__(self, jsonld: Optional[Dict[str, Any]] = None) -> None:
        if jsonld is not None:
            self.from_jsonld(jsonld)
        else:
            self.root = RootDataEntity()
            self.default_entities = [self.root, ROCrateMetadata(root=self.root)]
            self.data_entities = []
            self.contextual_entities = []

        self.root["hasPart"] = self.data_entities

    def add(self, *entities: Entity) -> None:
        for entity in entities:
            if isinstance(entity, DefaultEntity):
                raise UnexpectedImplementationError(f"DefaultEntity {self} can't be added to the crate.")
            if isinstance(entity, DataEntity):
                self.data_entities.append(entity)
            elif isinstance(entity, ContextualEntity):
                self.contextual_entities.append(entity)
            else:
                raise UnexpectedImplementationError("Invalid entity type")

    def delete(self, entity: Entity) -> None:
        if entity not in self.get_all_entities():
            raise UnexpectedImplementationError(f"Entity {entity} is not included in this crate.")

        if isinstance(entity, DefaultEntity):
            raise UnexpectedImplementationError(f"DefaultEntity {self} can't be removed from the crate.")
        if isinstance(entity, DataEntity):
            self.data_entities.remove(entity)
        elif isinstance(entity, ContextualEntity):
            self.contextual_entities.remove(entity)
        else:
            raise UnexpectedImplementationError("Invalid entity type")

    def get_by_id(self, entity_id: str) -> List[Entity]:
        entity_list: List[Entity] = []
        for ent in self.get_all_entities():
            if ent.id == entity_id:
                entity_list.append(ent)
        return entity_list

    def get_by_entity_type(self, entity: Type[Entity]) -> List[Entity]:
        entity_list: List[Entity] = []
        for ent in self.get_all_entities():
            if type(ent) is entity:
                entity_list.append(ent)
        return entity_list

    def get_all_entities(self) -> List[Entity]:
        return self.default_entities + self.data_entities + self.contextual_entities  # type:ignore

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_duplicate_entity()
        self.check_existence_of_entity()
        # `datePublished` field is defined in the RO-Crate specification.
        self.root["datePublished"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

        check_error = CheckPropsError()
        graph = []
        for e in self.get_all_entities():
            try:
                graph.append(e.as_jsonld())
            except EntityError as e:
                check_error.add_error(e)

        if len(check_error.entity_errors) > 0:
            raise check_error

        return {
            "@context": self.BASE_CONTEXT,
            "@graph": graph
        }

    def check_duplicate_entity(self) -> None:
        """\
        Check for duplicate entities in the RO-Crate.

        Duplicates, i.e. entities with the same `@id`, are allowed in the JSON-LD specification.
        For example, a `File` entity in the `base` context and a `File` entity in the `amed` context can have the same `@id` and be included in the crate.
        This is because the `name` property in each context is treated as different properties, even if they have the same `name` property.
        However, if two entities with the same `@id` and `@context` exist, and both have a `name` property with different values, it becomes unclear which one is correct.
        Therefore, this case is considered an error and an exception is raised.
        """
        id_context_list = []

        for ent in self.get_all_entities():
            id_context_list.append((ent.id, ent.context))

        dup_ents = [ent for ent, count in Counter(id_context_list).items() if count > 1]
        if len(dup_ents) > 0:
            raise CrateError(f"Duplicate @id and @context value found: {dup_ents}.")

    def check_existence_of_entity(self) -> None:
        for ent in self.get_all_entities():
            for val in ent.values():
                if isinstance(val, Entity) and val not in self.get_all_entities():
                    raise CrateError(f"The entity {val} is included in entity {ent}, but not included in the crate.")
                if isinstance(val, list):
                    # expected: [Any], [Entity]
                    for ele in [v for v in val if isinstance(v, Entity)]:
                        if ele not in self.get_all_entities():
                            raise CrateError(f"The entity {ele} is included in entity {ent}, but not included in this crate.")

    def dump(self, path: str) -> None:
        """\
        Dump the RO-Crate to the specified path.
        """
        with Path(path).resolve().open(mode="w", encoding="utf-8") as f:
            json.dump(self.as_jsonld(), f, indent=2,)

    def validate(self) -> None:
        governance_error = GovernanceError()

        for ent in self.get_all_entities():
            if isinstance(ent, ROCrateMetadata):
                continue
            try:
                ent.validate(self)
            except EntityError as e:
                governance_error.add_error(e)

        if len(governance_error.entity_errors) > 0:
            raise governance_error

    def from_jsonld(self, jsonld: Dict[str, Any]) -> None:
        # self.root = RootDataEntity()
        # self.default_entities = [self.root, ROCrateMetadata(root=self.root)]
        # self.data_entities = []
        # self.contextual_entities = []
        # self.root["hasPart"] = self.data_entities
        if "@graph" not in jsonld:
            raise CrateError("The JSON-LD doesn't have `@graph` property.")

        root_entity = None
        metadata_entity = None
        self.data_entities = []
        self.contextual_entities = []
        for entity in jsonld["@graph"]:
            id_ = entity.get("@id", None)
            if id_ is None:
                raise CrateError("The JSON-LD includes an entity without `@id` property.")
            type_ = entity.get("@type", None)
            if type_ is None:
                raise CrateError("The entity {id_} doesn't have `@type` property.")

            if id_ == "./" and type_ == "Dataset":
                root_entity = entity
            elif id_ == "ro-crate-metadata.json" and type_ == "CreativeWork":
                metadata_entity = entity
            else:
                context = entity.get("@context", None)
                if context is None:
                    raise CrateError("The entity <{type_} {id_}> doesn't have `@context` property.")
                schema_name = urlparse(context).path.split("/")[-1].split(".")[0]
                entity_class = import_entity_class(schema_name, type_)
                # TODO: 何かしらの抽象化層が必要
                props = deepcopy(entity)
                props.pop("@id")
                props.pop("@type")
                props.pop("@context")
                entity_instance = entity_class(id=id_, props=props)
                if isinstance(entity_instance, DataEntity):
                    self.data_entities.append(entity_instance)
                elif isinstance(entity_instance, ContextualEntity):
                    self.contextual_entities.append(entity_instance)
                else:
                    raise CrateError(f"Unknown entity type: {type(entity_instance)}")

        if root_entity is None:
            raise CrateError("The JSON-LD doesn't have root entity.")
        if metadata_entity is None:
            raise CrateError("The JSON-LD doesn't have metadata entity.")

        root_entity.pop("@id")
        root_entity.pop("@type")
        self.root = RootDataEntity(props=root_entity)
        metadata_entity.pop("@id")
        metadata_entity.pop("@type")
        self.default_entities = [self.root, ROCrateMetadata(root=self.root)]
