#!/usr/bin/env python3
# coding: utf-8

"""
Error classes for the RO-Crate and its entities.

This module contains the following error classes:

- EntityError: Error class for entities (checking entities in the crate).
- CrateError: Error class for the RO-Crate (checking the crate).
- CrateCheckPropsError: Error class for 'check_props()' method in the RO-Crate.
- CrateValidationError: Error class for 'validate()' method in the RO-Crate.
"""

from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from nii_dg.entity import Entity


class EntityError(Exception):
    """
    Error class for entities (checking entities in the crate).

    This error is raised during the Data Governance validation time, in the Entity 'check_props()' and 'validate()' methods.
    """

    def __init__(self, entity: "Entity") -> None:
        self.entity = entity
        self.errors: Dict[str, str] = {}

    def __str__(self) -> str:
        return f"EntityError: Errors occurred in {self.entity}: {self.errors}"

    def add(self, prop: str, msg: str) -> None:
        """
        Add an error message to the error dictionary.

        Args:
            prop (str): Property associated with the error.
            msg (str): Error message to add.
        """
        self.errors[prop] = msg

    def has_error(self) -> bool:
        """
        Return a boolean indicating whether there are errors.

        Returns:
            bool: True if there are errors, False otherwise.
        """
        return len(self.errors) != 0


class CrateError(Exception):
    """
    Error class for the RO-Crate (checking the crate).

    This error is raised during the Data Governance validation time.
    """


class CrateCheckPropsError(CrateError):
    """
    Error class for 'check_props()' method in the RO-Crate.

    This error is raised during the Data Governance validation time, during the validation performed by the 'check_props()' method of the ROCrate class.
    """

    def __init__(self, errors: List[EntityError] = []) -> None:
        self.errors = errors

    def __str__(self) -> str:
        error_msg = "\n".join([f"- {e}" for e in self.errors])
        return (
            "CrateCheckPropsError: Errors occurred in check_props() for entities:\n\n"
            + error_msg
        )

    def add(self, *errors: EntityError) -> None:
        self.errors.extend(errors)

    def has_error(self) -> bool:
        """
        Return a boolean indicating whether there are errors.

        Returns:
            bool: True if there are errors, False otherwise.
        """
        return len(self.errors) != 0


class CrateValidationError(CrateError):
    """
    Error class for 'validate()' method in the RO-Crate.

    This error is raised during the Data Governance validation time, during the validation performed by the 'validate()' method of the ROCrate class.
    """

    errors: List[EntityError]

    def __init__(self, errors: List[EntityError] = []):
        self.errors = errors

    def __str__(self) -> str:
        error_msg = "\n".join([f"- {e}" for e in self.errors])
        return (
            "CrateValidationError: Errors occurred in validate() for entities:\n\n"
            + error_msg
        )

    def add(self, *errors: EntityError) -> None:
        self.errors.extend(errors)

    def has_error(self) -> bool:
        """
        Return a boolean indicating whether there are errors.

        Returns:
            bool: True if there are errors, False otherwise.
        """
        return len(self.errors) != 0
