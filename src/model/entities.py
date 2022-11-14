from datetime import datetime
from zoneinfo import ZoneInfo

class Entity():

    def __init__(self):
        self._jsonld = self._empty()

    def _empty(self):
        pass

    def get_jsonld(self):
        return self._jsonld

class ContextEntity(Entity):

    def __init__(self):
        super().__init__()    


class DataEntity(Entity):

    def __init__(self):
        super().__init__()


class RootDataEntity(DataEntity):
    id = './'

    def __init__(self):
        super().__init__()

    def _empty(self):

        val = {
            "@id": self.id,
            "@type": "Dataset",
            "datePublished": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
        }
        return val


class Metadata(Entity):
    BASENAME = "ro-crate-metadata.json"
    PROFILE = "https://w3id.org/ro/crate/1.1"

    def __init__(self):
        super().__init__()
    
    def _empty(self):
        val = {"@id": self.BASENAME,
                "@type": "CreativeWork",
                "conformsTo": {"@id": self.PROFILE},
                "about": {"@id": "./"}}
        return val