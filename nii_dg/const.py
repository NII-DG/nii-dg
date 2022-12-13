#!/usr/bin/env python3

from typing import Dict, List

"""
from RO-Crate definition
"""
BASENAME: str = "ro-crate-metadata.json"
PROFILE: str = "https://w3id.org/ro/crate/1.1"

"""
NII RO-Crate Original
"""
EXTRA_TERMS: Dict[str, str] = {
    "accessRights": "http://purl.org/dc/terms/accessRights",
    "dmpFormat": "https://example.com/dmpFormat",  # to be updated
    "dmpDataNumber": "https://example.com/dataManagementPlan"  # to be updated
}
FREEACCESS: Dict[str, str] = {"free": "true", "consideration": "false"}

DMPSTYLES: List[str] = [
    "common_metadata",
    "JST",
    "AMED",
    "METI"
]
