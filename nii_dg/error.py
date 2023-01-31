#!/usr/bin/env python3
# coding: utf-8
import ast
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from nii_dg.entity import Entity


class UnexpectedImplementationError(Exception):
    """\
    Error class for unexpected implementation.
    This library is intended to be added to implementations under schema directory. (e.g., amed.py)
    In addition, users can generate a RO-Crate by using this library.
    Therefore, this error is raised when the implementation is not as expected.
    """


class PropsError(Exception):
    """\
    Error class for props (checking for entity properties).
    Raised at Entity dump time.
    This validation is performed by the check_props() method (this method is called in as_jsonld()).
    """


class EntityError(Exception):
    """\
    Error class for entity (checking for entities in crate).
    Raised at Data Governance validation time at Entity validate() method.
    This validation is called by RO-Crate validate() method.
    """

    def __init__(self, entity: "Entity") -> None:
        self.entity = entity
        self.message_dict: Dict[str, str] = {}

    def __str__(self) -> str:
        return str({repr(self.entity): self.message_dict})

    def __repr__(self) -> str:
        return str({repr(self.entity): self.message_dict})

    def add(self, prop: str, message: str) -> None:
        self.message_dict.setdefault(prop, message)

    def update(self, messages: str) -> None:
        self.message_dict.update(ast.literal_eval(messages))


class CrateError(Exception):
    """\
    Error class for rocrate (checking for crate).
    Raised at ROCrate dump time and Data Governance validation time.
    The dump is performed by the check_entities() method (this method is called in dump()) of ROCrate class.
    The validation is performed by the validate() method of each subclass.
    """


class CheckPropsError(Exception):
    """\
    Error class for checking properties of each included entities.
    Raised at ROCrate dump time.
    The dump is performed by the as_jsonld() method (this method is called in dump()) of ROCrate class.
    The check is performed by the check_props() method of each subclass.
    """

    def __init__(self, entity_errors: Optional[List[EntityError]] = None) -> None:
        if entity_errors:
            self.entity_errors = entity_errors
        else:
            self.entity_errors = []

    def __str__(self) -> str:
        return "Property-check failures:" + str(self.entity_errors)

    def add_error(self, entity_error: EntityError) -> None:
        self.entity_errors.append(entity_error)


class GovernanceError(Exception):
    """\
    Error class for governance (validating for data governance).
    Raised at Data Governance validation time at RO-Crate validate() method.
    This validation is performed by the validate() method of each subclass.
    For each subclass, EntityError is raised when the validation fails.

    - Error として複数の entity から送出された error (Entity error) がまとめられる
    - それぞれの元となる entity の情報も持っていてほしい (included in entity error)
    - また、まとめられた error list を summarize するメソッドもほしい
    """

    def __init__(self, entity_errors: Optional[List[EntityError]] = None) -> None:
        if entity_errors:
            self.entity_errors = entity_errors
        else:
            self.entity_errors = []

    def __str__(self) -> str:
        return "Validation failures:" + str(self.entity_errors)

    def add_error(self, entity_error: EntityError) -> None:
        self.entity_errors.append(entity_error)
