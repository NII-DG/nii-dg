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
                raise TypeError("Invalid entity type")  # TODO: define exception

    def get(self, entity_id: str) -> Optional[Entity]:
        for ent in self.default_entities + self.data_entities + self.contextual_entities:
            if ent.id == entity_id:
                return ent
        return None

    def get_entities(self, entity: Type[Entity]) -> List[Entity]:
        entity_list: List[Entity] = []
        for ent in self.default_entities + self.data_entities + self.contextual_entities:
            if type(ent) is entity:
                entity_list.append(ent)
        return entity_list

    def as_jsonld(self) -> Dict[str, Any]:
        self.check_entities()
        # add dateCreated to RootDataEntity
        self.root["dateCreated"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        return {
            "@context": self.BASE_CONTEXT,
            "@graph": [e.as_jsonld() for e in self.default_entities + self.data_entities + self.contextual_entities]  # type: ignore
        }

    def check_entities(self) -> None:
        id_context_list = []
        for ent in self.default_entities + self.data_entities + self.contextual_entities:
            id_context_list.append((ent.id, ent.context))
        dup_ents = [ent for ent, count in Counter(id_context_list).items() if count > 1]
        if len(dup_ents) > 0:
            raise ValueError(f"Duplicate @id and @context value found: {dup_ents}.")

    def dump(self, path: str) -> None:
        """\
        Dump the RO-Crate to the specified path.
        """
        with Path(path).resolve().open("w") as f:
            json.dump(self.as_jsonld(), f, width=1000, indent=2,)
