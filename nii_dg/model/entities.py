from datetime import datetime
from zoneinfo import ZoneInfo


class Entity():

    def __init__(self, id_=None, type_=None):
        self.id = id_
        self.type = type_
        self._jsonld = self._empty()

    def _empty(self):
        val = {
            "@id": self.id,
            "@type": self.type
        }
        return val

    def get_jsonld(self):
        return self._jsonld

    def set_name(self, name):
        self._jsonld['name'] = name

    def add_properties(self, properties):
        self._jsonld |= properties

    def get(self, property_name):
        return self._jsonld.get(property_name)


class ContextEntity(Entity):

    def __init__(self, id_=None, type_=None):
        super().__init__(id_, type_)


class DataEntity(Entity):

    def __init__(self, id_=None, type_=None):
        super().__init__(id_, type_)


class RootDataEntity(DataEntity):

    def __init__(self, id_='./', type_='Dataset'):
        super().__init__(id_, type_)

    def _empty(self):
        val = {
            "@id": self.id,
            "@type": self.type,
            "datePublished": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
        }
        return val


class Metadata(Entity):
    BASENAME = "ro-crate-metadata.json"
    PROFILE = "https://w3id.org/ro/crate/1.1"

    def __init__(self, id_=None, type_='CreativeWork'):
        super().__init__(id_, type_)
        self.id = self.BASENAME

    def _empty(self):
        val = {"@id": self.BASENAME,
               "@type": self.type,
               "conformsTo": {"@id": self.PROFILE},
               "about": {"@id": "./"}}
        return val
