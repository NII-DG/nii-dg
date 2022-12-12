'''
from RO-Crate definition
'''

BASENAME: str = "ro-crate-metadata.json"
PROFILE: str = "https://w3id.org/ro/crate/1.1"

'''
NII RO-Crate Original
'''
EXTRA_TERMS: dict[str, str] = {
    "accessRights": "http://purl.org/dc/terms/accessRights",
    "dmpFormat": "https://example.com/dmpFormat",  # to be updated
    "dmpDataNumber": "https://example.com/dataManagementPlan"  # to be updated
}
FREEACCESS: dict[str, str] = {"free": "true", "consideration": "false"}

DMPSTYLES: list[str] = [
    "common_metadata",
    "JST",
    "AMED",
    "METI"
]
