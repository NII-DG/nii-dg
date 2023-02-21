#!/usr/bin/env python3
# coding: utf-8
import ast
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from nii_dg.entity import Entity


class UnexpectedImplementationError(Exception):
    """\
    Error class for unexpected implementation.
    This library is intended to be added to implementations under the schema directory (e.g., `amed.py`).
    That is, this error is raised when these additional implementations are not as expected.
    """


class PropsError(Exception):
    """\
    Error class for props (checking entity properties).
    This error is raised during the Entity dump time, during the validation performed by the `check_props()` method (which is called in the `as_jsonld()` method).
    """


class EntityError(Exception):
    """\
    Error class for entities (checking entities in the crate).
    This error is raised during the Data Governance validation time, in the Entity `validate()` method.
    This validation is performed by the RO-Crate `validate()` method.
    """

    def __init__(self, entity: "Entity") -> None:
        self.entity = entity
        self.message_dict: Dict[str, str] = {}

    def __str__(self) -> str:
        return str({repr(self.entity): self.message_dict})

    def __repr__(self) -> str:
        return str({repr(self.entity): self.message_dict})

    def add(self, prop: str, message: str) -> None:
        """\
        Add a message to the message dictionary.
        """
        self.message_dict.setdefault(prop, message)

    def add_by_dict(self, messages: str) -> None:
        """\
        Add messages from a dictionary to the message dictionary.
        """
        # TODO: check this implementation (looks like a hack)
        message_dict = ast.literal_eval(messages)
        for key, value in zip(message_dict.keys(), message_dict.values()):
            self.message_dict.setdefault(key, value)


class CrateError(Exception):
    """\
    Error class for the RO-Crate (checking the crate).
    This error is raised during the RO-Crate dump time and Data Governance validation time.
    The dump is performed by the `check_entities()` method (which is called in the `dump()` method) of the ROCrate class.
    The validation is performed by the `validate()` method of each subclass.
    """


class CheckPropsError(Exception):
    """\
    Error class for checking properties of included entities.
    This error is raised during the RO-Crate dump time, during the validation performed by the `as_jsonld()` method (which is called in the `dump()` method) of the ROCrate class.
    The check is performed by the `check_props()` method of each subclass.
    """

    def __init__(self, entity_errors: Optional[List[EntityError]] = None) -> None:
        """\
        Initialize with a list of entity errors.
        """
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
