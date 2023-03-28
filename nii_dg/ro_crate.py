#!/usr/bin/env python3
# coding: utf-8

"""\
Implementation of the RO-Crate class.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from nii_dg.const import DOWNLOADED_SCHEMA_DIR_NAME, RO_CRATE_CONTEXT
from nii_dg.entity import (ContextualEntity, DataEntity, DefaultEntity, Entity,
                           ROCrateMetadata, RootDataEntity)
from nii_dg.error import (CrateCheckPropsError, CrateError,
                          CrateValidationError, EntityError)
from nii_dg.module_info import GH_REF, GH_REPO
from nii_dg.utils import download_schema, import_custom_class, parse_ctx


class ROCrate():
    """\
    Class representing a Research Object Crate (RO-Crate).

    A RO-Crate is a packaging format for research data that aims to make it easier to share and reuse.

    The class provides methods for adding and removing entities, as well as for dumping the RO-Crate to a file.

    The entities are divided into three types:

    - DefaultEntity: An entity that is always included in the RO-Crate, e.g., ROCrateMetadata, RootDataEntity.
    - DataEntity: An entity that represents a file or directory, e.g., File, Dataset.
    - ContextualEntity: An entity that represents metadata, e.g., Person, License.

    Each entity inherits from the Entity class and is defined in entity.py.

    For more details on the RO-Crate specification, please refer to https://www.researchobject.org/ro-crate/.

    Attributes:
        default_entities (List[DefaultEntity]): A list of default entities.
        data_entities (List[DataEntity]): A list of data entities.
        contextual_entities (List[ContextualEntity]): A list of contextual entities.
        root (RootDataEntity): The root data entity.
    """

    default_entities: List[DefaultEntity]
    data_entities: List[DataEntity]
    contextual_entities: List[ContextualEntity]
    root: RootDataEntity

    def __init__(self, jsonld: Optional[Dict[str, Any]] = None) -> None:
        """\
        Initialize a new instance of the RO-Crate class.

        Args:
            jsonld (Optional[Dict[str, Any]]): The JSON-LD data to use for initializing the RO-Crate.

        Raises:
            TypeError: If the entity type is not supported.
        """
        if jsonld is not None:
            self.from_jsonld(jsonld)
        else:
            self.root = RootDataEntity()
            self.default_entities = [self.root, ROCrateMetadata()]
            self.data_entities = []
            self.contextual_entities = []

        self.root["hasPart"] = self.data_entities

    def add(self, *entities: Entity) -> None:
        """\
        Add entities to the RO-Crate.

        Args:
            *entities (Entity): The entities to be added to the RO-Crate.

        Raises:
            TypeError: If the entity type is not supported.
        """
        for entity in entities:
            if isinstance(entity, DefaultEntity):
                self.default_entities.append(entity)
            elif isinstance(entity, DataEntity):
                self.data_entities.append(entity)
            elif isinstance(entity, ContextualEntity):
                self.contextual_entities.append(entity)
            else:
                raise TypeError("'Entity' class is not supported to be added directly. Please use 'DefaultEntity', 'DataEntity', or 'ContextualEntity' instead.")

    def remove(self, *entities: Entity) -> None:
        """\
        Removes entities from the RO-Crate.

        Args:
            *entities: The entities to be removed from the RO-Crate.

        Raises:
            ValueError: If the entity is not included in the RO-Crate or is a DefaultEntity.
            TypeError: If the entity type is not supported.

        Note:
            There are three types of entities that can be removed: DefaultEntity, DataEntity, and ContextualEntity.
            If an unsupported entity is given, a TypeError is raised.
            If the entity is not included in the RO-Crate, a ValueError is raised.
        """
        for entity in entities:
            if entity not in self.all_entities:
                raise ValueError(f"Entity {entity} is not included in the RO-Crate.")

            if isinstance(entity, DefaultEntity):
                raise ValueError(f"Entity {entity} is a DefaultEntity and cannot be removed.")
            elif isinstance(entity, DataEntity):
                self.data_entities.remove(entity)
            elif isinstance(entity, ContextualEntity):
                self.contextual_entities.remove(entity)
            else:
                raise TypeError("'Entity' class is not supported to be removed directly. Please use 'DefaultEntity', 'DataEntity', or 'ContextualEntity' instead.")

    @property
    def all_entities(self) -> List[Entity]:
        """\
        Get all entities in the RO-Crate.

        Returns:
            A list of all entities in the RO-Crate.
        """
        return self.default_entities + self.data_entities + self.contextual_entities  # type: ignore

    def get_by_id(self, id_: str) -> List[Entity]:
        """\
        Get entities by ID.

        Args:
            id_: The ID of the entity.

        Returns:
            A list of entities with the specified ID.
        """
        return [entity for entity in self.all_entities if entity.id == id_]

    def get_by_type(self, type_: str) -> List[Entity]:
        """\
        Get entities by type.

        Args:
            type_: The type of the entity.

        Returns:
            A list of entities with the specified type.
        """
        return [entity for entity in self.all_entities if entity.type == type_]

    def from_jsonld(self, jsonld: Dict[str, Any]) -> None:
        """\
        Deserialize an RO-Crate from JSON-LD.

        Args:
            jsonld (Dict[str, Any]): The JSON-LD data to deserialize.

        Raises:
            TypeError: If the JSON-LD data is not a dictionary.
            ValueError: If the JSON-LD data does not have the required keys or values.
            ValueError: If a required RootDataEntity and ROCrateMetadata entity is not found.
            ValueError: If an entity type is not found.
        """
        if not isinstance(jsonld, dict):
            raise TypeError("The JSON-LD data must be a dictionary.")
        if "@context" not in jsonld:
            raise ValueError("The JSON-LD data must have a '@context' key.")
        if jsonld["@context"] != RO_CRATE_CONTEXT:
            raise ValueError("The JSON-LD data must have the RO-Crate context.")
        if "@graph" not in jsonld:
            raise ValueError("The JSON-LD data must have a '@graph' key.")

        root_data_entity = None
        metadata_entity = None
        self.default_entities = []
        self.data_entities = []
        self.contextual_entities = []

        for entity in jsonld["@graph"]:
            id_ = entity.get("@id")
            if id_ is None:
                raise ValueError("The JSON-LD data must have an '@id' key for each entity.")
            type_ = entity.get("@type")
            if type_ is None:
                raise ValueError("The JSON-LD data must have an '@type' key for each entity.")

            if id_ == "./" and type_ == "Dataset":
                root_data_entity = RootDataEntity.from_jsonld(entity)
            elif id_ == "ro-crate-metadata.json" and type_ == "CreativeWork":
                metadata_entity = ROCrateMetadata.from_jsonld(entity)
            else:
                ctx = entity.get("@context", RO_CRATE_CONTEXT)
                gh_repo, gh_ref, schema = parse_ctx(ctx)
                if gh_repo != GH_REPO:
                    # TODO: support other github repositories or not?
                    raise ValueError(f"The context {ctx} which is generated by {gh_repo} is not supported.")
                entity_class = None
                if gh_ref != GH_REF:
                    # TODO: check gh_ref is semver or not? using is_semantic_version()
                    # TODO: check newer version is available or not? using is_newer_version()
                    # TODO: download context file, them download schema file or not?
                    download_schema(gh_repo, gh_ref, schema)
                    entity_class = import_custom_class(f".{DOWNLOADED_SCHEMA_DIR_NAME}.{gh_repo}.{gh_ref}.{schema}", type_)
                else:
                    entity_class = import_custom_class(f"nii_dg.schema.{schema}", type_)
                if entity_class is None:
                    raise ValueError(f"Entity type {type_} is not found.")
                entity_instance = entity_class.from_jsonld(entity)
                if isinstance(entity_instance, DataEntity):
                    self.data_entities.append(entity_instance)
                elif isinstance(entity_instance, ContextualEntity):
                    self.contextual_entities.append(entity_instance)
                else:
                    raise ValueError(f"Entity type {type_} is not supported.")

        if root_data_entity is None:
            raise ValueError("The JSON-LD data must have a RootDataEntity.")
        if metadata_entity is None:
            raise ValueError("The JSON-LD data must have a ROCrateMetadata entity.")

        self.root = root_data_entity  # type: ignore
        self.default_entities = [self.root, metadata_entity]  # type: ignore

    def as_jsonld(self) -> Dict[str, Any]:
        """\
        Serialize the RO-Crate as JSON-LD.

        Returns:
            Dict[str, Any]: The serialized RO-Crate as JSON-LD.
        """
        self.check_duplicate_entity()
        self.check_props()

        return {
            "@context": RO_CRATE_CONTEXT,
            "@graph": [entity.as_jsonld() for entity in self.all_entities]
        }

    def dump(self, path: str) -> None:
        """\
        Dump the RO-Crate to a file.

        Args:
            path (str): The path to the file to dump the RO-Crate to.
        """
        with Path(path).resolve().open("w", encoding="utf-8") as f:
            json.dump(self.as_jsonld(), f, indent=2)

    def check_duplicate_entity(self) -> None:
        """\
        Check for duplicate entities in the RO-Crate.

        Duplicate entities, that is, entities with the same '@id' value, are allowed in the JSON-LD specification.
        For example, a 'File' entity in the 'base' context and a 'File' entity in the 'amed' context can have the same '@id' value.
        This is because the 'name' property in each context is treated as a different property.
        However, if two entities have the same '@id' value and '@context' value, and both have 'name' property with different values, it becomes unclear which one is correct.
        Therefore, this case ('@id' and '@context' are same) is considered as an error and an exception is raised.

        Raises:
            CrateError: If there are duplicate entities in the RO-Crate.
        """
        id_ctx = [(entity.id, entity.context) for entity in self.all_entities]
        dup_id_ctx = [id_ctx[i] for i in range(len(id_ctx)) if id_ctx.count(id_ctx[i]) > 1]
        if len(dup_id_ctx) > 0:
            raise CrateError(f"Duplicate entities are found in the RO-Crate: {dup_id_ctx}")

    def check_props(self) -> None:
        """\
        Check the properties of all entities in the RO-Crate.

        Raises:
            CrateCheckPropsError: If there are errors in the properties of the entities.
        """
        crate_error = CrateCheckPropsError()
        for entity in self.all_entities:
            try:
                entity.check_props()
            except EntityError as e:
                crate_error.add(e)
            except Exception as e:
                raise e

        if crate_error.has_error():
            raise crate_error

    def validate(self) -> None:
        """\
        Validate the RO-Crate.

        Raises:
            CrateValidationError: If there are errors in the entities in the RO-Crate.
        """
        crate_error = CrateValidationError()
        for entity in self.all_entities:
            try:
                entity.validate(self)
            except EntityError as e:
                crate_error.add(e)
            except Exception as e:
                raise e

        if crate_error.has_error():
            raise crate_error
