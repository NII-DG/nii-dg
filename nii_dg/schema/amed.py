#!/usr/bin/env python3
# coding: utf-8

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from nii_dg.entity import ContextualEntity, DataEntity, DefaultEntity, Entity
from nii_dg.schema import (DataDownload, HostingInstitution, Organization,
                           Person, RepositoryObject)
from nii_dg.schema import RootDataEntity as BaseRootDataEntity
from nii_dg.utils import github_branch, github_repo


def check_type(ent: Entity, key: str, type: Union[type, List[type]]) -> None:
    if isinstance(type, list):
        for e in ent[key]:
            if not isinstance(e, type[0]):
                raise TypeError("Elements of '{key}' list MUST be {typename}.".format(
                    key=key,
                    typename=type[0].__name__
                ))
    else:
        if not isinstance(ent[key], type):
            raise TypeError("The value of '{key}' MUST be {typename}.".format(
                key=key,
                typename=type.__name__
            ))


def check_required_key(ent: Entity, key: str) -> None:
    try:
        ent[key]
    except KeyError:  # define validation error
        raise TypeError("The required term '{key}' is not found in the {entity}.".format(
            key=key,
            entity=ent.__class__.__name__
        )) from None



class RootDataEntity(BaseRootDataEntity):
    """\
    See https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity.
    """

    def __init__(self, props: Optional[Dict[str, Any]] = None):
        super().__init__()

    def check_props(self) -> None:
        '''
        Check properties based on the schema of RootDataEntity.
        - @id: Set './' at the constructor. No checl is done here.
        - name: Required. MUST be string.
        - description: Optional. MUST be string.
        - funder: Required. MUST be an array of Organization entity.
        - funding: Required. MUST be string.
        - chiefResearcher: Required. MUST be Person entity.
        - dateCreated: 自動生成?
        - creator: Required. Must be an array of Person entity.
        - hostingInstitution: Required. MUST be Organization entity.
        - dataManager: Required. Must be Person entity.
        - repository: Required. Must be RepositoryObject entity.
        - distribution: Optional. Must be DataDownload entity.
        - hasPart: Will be set at RO-Crate Class. No check is done here.
        '''
        required_keys: Dict[str, Union[type, List[type]]] = {
            "name": str,
            "funder": [Organization],
            "funding": str,
            "chiefResearcher": Person,
            "creator": [Person],
            "hostingInstitution": HostingInstitution,
            "dataManager": Person
        }
        optional_keys: Dict[str, Union[type, List[type]]] = {
            "description": str,
            "repository": RepositoryObject,
            "distribution": DataDownload
        }

        for k in required_keys:
            check_required_key(self, k)

        for k, v in {**required_keys, **optional_keys}.items():
            try:
                check_type(self, k, v)
            except KeyError:
                pass

    def validate(self) -> None:
        # TODO: impl.
        pass
