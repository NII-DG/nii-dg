from datetime import datetime
from zoneinfo import ZoneInfo
import const

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

    def __init__(self):
        super().__init__()
    
    def _empty(self):
        val = {"@id": const.BASENAME,
                "@type": "CreativeWork",
                "conformsTo": {"@id": const.PROFILE},
                "about": {"@id": "./"}}
        return val