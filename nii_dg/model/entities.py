from datetime import datetime,timezone, timedelta
from nii_dg import const


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
        self._jsonld.update(properties)

    def get(self, property_name):
        return self._jsonld.get(property_name)

    def get_id_dict(self) -> dict:
        return {"@id":self.get("@id")}


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
            "datePublished": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        }
        return val


class Metadata(Entity):

    def __init__(self, id_=const.BASENAME, type_='CreativeWork'):
        super().__init__(id_, type_)

    def _empty(self):
        val = {"@id": self.id,
               "@type": self.type,
               "conformsTo": {"@id": const.PROFILE},
               "about": {"@id": "./"}}
        return val
