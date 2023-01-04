#!/usr/bin/env python3
# coding: utf-8

"""\
Definition of Entity base class and its subclasses.
"""

from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Dict, Optional

from nii_dg.utils import github_branch, github_repo

if TYPE_CHECKING:
    TypedMutableMapping = MutableMapping[str, Any]
else:
    TypedMutableMapping = MutableMapping


class Entity(TypedMutableMapping):
    """\
    Base class for all entities.

    By inheriting MutableMapping, this class implements the following methods:
    `__contains__`, `__eq__`, `__ne__`, `get`, `pop`, `popitem`, `setdefault`, `update`, `clear`, `keys`, `values` and `items`.
    """

    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None) -> None:
        self.data: Dict[str, Any] = {}

        self["@id"] = id
        self["@type"] = self.__class__.__name__
        # self["@context"] = TODO
        self.update(props or {})

    def __setitem__(self, key: str, value: Any) -> None:
        # TODO: @context, @id, @type は書き換え不可にする
        self.data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __delitem__(self, key: str) -> None:
        if key.startswith("@"):
            raise KeyError(f"Cannot delete reserved key: {key}")
        del self.data[key]

    def __iter__(self) -> Any:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"<{self.type} {self.id}>"

    @property
    def id(self) -> str:
        return self.data["@id"]  # type: ignore

    @property
    def type(self) -> str:
        return self.data["@type"]  # type: ignore

    def as_jsonld(self) -> Dict[str, Any]:
        """\
        Dump this entity as JSON-LD.
        Basically, it is assumed that self.check_props method checks the existence of required props and the type of props.
        In addition, this method do the following:

        - Add context prop (not for ROCrateMetadata)
        - Replace entities in props with their id
        """
        ref_data: Dict[str, Any] = {}
        for key, val in self.items():
            if isinstance(val, dict):
                # expected: {"@id": str}, {"@value": Any}
                # These cannot be supported at this stage, should be supported in self.check_props.
                ref_data[key] = val
            elif isinstance(val, list):
                # expected: [Any], [Entity]
                ref_data[key] = [{"@id": v.id} if isinstance(v, Entity) else v for v in val]
            elif isinstance(val, Entity):
                ref_data[key] = {"@id": val.id}
            else:
                ref_data[key] = val
        if not isinstance(self, ROCrateMetadata):
            ref_data["@context"] = self.context
        return ref_data

    @property
    def context(self) -> str:
        template = "https://raw.githubusercontent.com/{repo}/{branch}/schema/context/{schema}/{entity}.json"
        return template.format(
            repo=github_repo(),
            branch=github_branch(),
            schema=self.schema,
            entity=self.type,
        )

    @property
    def schema(self) -> str:
        """\
        Implementation of this method is required in each subclass using comment-outed code.
        """
        # return Path(__file__).stem
        raise NotImplementedError

    def check_props(self) -> None:
        """\
        Called at RO-Crate dump time.
        Check if all required props are set and if prop types are correct.
        Implementation of this method is required in each subclass.
        """
        # Abstract method
        raise NotImplementedError

    def validate(self) -> None:
        """\
        Called at Data Governance validation time.
        Comprehensive validation including the value of props.
        Implementation of this method is required in each subclass.
        """
        # Abstract method
        raise NotImplementedError


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


class ROCrateMetadata(DefaultEntity):
    """\
    RO-Crate must contain a RO-Crate metadata file descriptor with the `@id` of `ro-crate-metadata.json`.

    See https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#ro-crate-metadata-file-descriptor.
    """

    def __init__(self, root: Entity) -> None:
        super().__init__(id="ro-crate-metadata.json")
        self["@type"] = "CreativeWork"
        self["conformsTo"] = {"@id": "https://w3id.org/ro/crate/1.1"}
        self["about"] = root
