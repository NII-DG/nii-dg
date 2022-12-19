#!/usr/bin/env python3
# coding: utf-8

"""\
Definition of Entity base class and its subclasses.
"""

from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Dict, Optional

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

    data: Dict[str, Any] = {}

    def __init__(self, id: str, props: Optional[Dict[str, Any]] = None) -> None:
        self["@id"] = id
        self["@type"] = self.__class__.__name__
        self.update(props or {})

    def __setitem__(self, key: str, value: Any) -> None:
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

    @property
    def id(self) -> str:
        return self.data["@id"]  # type: ignore

    @property
    def type(self) -> str:
        return self.data["@type"]  # type: ignore

    def dump_jsonld(self) -> Dict[str, Any]:
        # TODO: add context prop
        # TODO: treat entities in props
        pass

    def check_props(self) -> None:
        """\
        Called at RO-Crate dump time.
        Check if all required props are set and if prop types are correct.
        """
        # Abstract method
        raise NotImplementedError

    def validate(self) -> None:
        """\
        Called at Data Governance validation time.
        Comprehensive validation including the value of props.
        """
        # Abstract method
        raise NotImplementedError


class DefaultEntity(Entity):
    """\
    A entity that is always included in the RO-Crate. For example, ROCrateMetadata, RootDataEntity, etc.
    """

    pass


class DataEntity(Entity):
    """\
    A entity that represents a file or directory. For example, File, Dataset, etc.
    This entity is always included in RootDataset entity.
    """
    pass


class ContextualEntity(Entity):
    """\
    A entity that represents a metadata. For example, Person, License, etc.
    """
    pass
