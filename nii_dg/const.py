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
<<<<<<< HEAD
FREEACCESS: dict[str, str] = {"free": "true", "consideration": "false"}

DMPSTYLES: list[str] = [
=======
FREEACCESS = {"free": "true", "consideration": "false"}

DMPSTYLES = [
>>>>>>> 23b1b8b... Add github action and update README
    "common_metadata",
    "JST",
    "AMED",
    "METI"
]
