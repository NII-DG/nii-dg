from .entities import Entity, Dataentity, ContextEntity

class ROCrate():

    BASENAME = "ro-crate-metadata.json"
    PROFILE = "https://w3id.org/ro/crate/1.1"

    def __init__(self):
        self.metadata = {}