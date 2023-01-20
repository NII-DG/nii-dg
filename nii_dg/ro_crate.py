#!/usr/bin/env python3
# coding: utf-8

"""\
Definition of RO-Crate class.
"""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from nii_dg.entity import (ContextualEntity, DataEntity, DefaultEntity, Entity,
                           ROCrateMetadata)
from nii_dg.error import CrateError, EntityError, GovernanceError
from nii_dg.schema import RootDataEntity


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

    default_entities: List[DefaultEntity] = []
    data_entities: List[DataEntity] = []
    contextual_entities: List[ContextualEntity] = []

    root: RootDataEntity

    BASE_CONTEXT: str = "https://w3id.org/ro/crate/1.1/context"

    def __init__(self, from_jsonld: Optional[Dict[str, Any]] = None) -> None:
        self.root = RootDataEntity()
        self.root["hasPart"] = self.data_entities
        self.add(self.root, ROCrateMetadata(root=self.root))

    def add(self, *entities: Entity) -> None:
        for entity in entities:
            if isinstance(entity, DefaultEntity):
                self.default_entities.append(entity)
            elif isinstance(entity, DataEntity):
                self.data_entities.append(entity)
            elif isinstance(entity, ContextualEntity):
                self.contextual_entities.append(entity)
            else:
                raise EntityError("Invalid entity type")

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
        # add dateCreated to RootDataEntity
        self.root["dateCreated"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        return {
            "@context": self.BASE_CONTEXT,
            "@graph": [e.as_jsonld() for e in self.get_all_entities()]
        }

    def check_duplicate_entity(self) -> None:
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
                elif isinstance(val, list):
                    # expected: [Any], [Entity]
                    for ele in [v for v in val if isinstance(v, Entity)]:
                        if ele not in self.get_all_entities():
                            raise CrateError(f"The entity {ele} is included in entity {ent}, but not included in this crate.")

    def dump(self, path: str) -> None:
        """\
        Dump the RO-Crate to the specified path.
        """
        with Path(path).resolve().open("w") as f:
            json.dump(self.as_jsonld(), f, width=1000, indent=2,)

    def validate(self) -> None:
        for ent in self.get_all_entities():
            if isinstance(ent, ROCrateMetadata):
                continue
            ent.validate(self)
