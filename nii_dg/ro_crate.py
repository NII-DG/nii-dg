#!/usr/bin/env python3
# coding: utf-8

"""\
Definition of RO-Crate class.
"""

from typing import List

from nii_dg.entity import ContextualEntity, DataEntity, DefaultEntity, Entity


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

    BASE_CONTEXT: str = "https://w3id.org/ro/crate/1.1/context"

    def __init__(self) -> None:
        self.add(ROCrateMetadata())

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


class ROCrateMetadata(DefaultEntity):
    """\
    RO-Crate must contain a RO-Crate metadata file descriptor with the `@id` of `ro-crate-metadata.json`.

    See https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#ro-crate-metadata-file-descriptor.
    """

    ID = "ro-crate-metadata.json"
    TYPE = "CreativeWork"
    CONFORMS_TO = "https://w3id.org/ro/crate/1.1"

    def __init__(self) -> None:
        super().__init__(id=self.ID)
        self["@type"] = self.TYPE
        self["conformsTo"] = {"@id": self.CONFORMS_TO}
        self["about"] = {"@id": "./"}
