#!/usr/bin/env python3
# coding: utf-8
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from nii_dg.entity import Entity


class UnexpectedImplementationError(Exception):
    """\
    Error class for unexpected implementation.
    This library is intended to be added to implementations under schema directory. (e.g., amed.py)
    In addition, users can generate a RO-Crate by using this library.
    Therefore, this error is raised when the implementation is not as expected.
    """
    pass


class PropsError(Exception):
    """\
    Error class for props (checking for entity properties).
    Raised at Entity dump time.
    This validation is performed by the check_props() method (this method is called in dump()) of each subclass.
    """
    pass


class GovernanceError(Exception):
    """\
    Error class for governance (validating for data governance).
    Raised at Data Governance validation time.
    This validation is performed by the validate() method of each subclass.
    """
    pass
    # def __init__(self, entity: "Entity") -> None:
    #     self.entity = entity
    #     self.failure_dict: Dict[str, str] = {}

    # def __str__(self) -> str:
    #     return str({repr(self.entity): self.failure_dict})

    # def add(self, prop: str, message: str) -> None:
    #     self.failure_dict.setdefault(prop, message)


class EntityError(Exception):
    """\
    Error class for entity (checking for entities in crate).
    Raised at Entity addition time.
    The validation is performed by the validate() method of ROCrate class and each subclass.
    The addition is performed by the add() method of ROCrate class.
    """
    pass


class CrateError(Exception):
    """\
    Error class for rocrate (checking for crate).
    Raised at ROCrate dump time.
    This validation is performed by the check_entities() method (this method is called in dump()) of ROCrate class.
    """
    pass
    # def __init__(self, message: str, rocrate: "ROCrate", entity: "Entity" = None):
    #     super().__init__(message)
    #     self.rocrate = rocrate
    #     self.entity = entity
