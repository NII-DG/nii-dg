from datetime import datetime,timezone
from nii_dg import const


class Entity():
    '''
    エンティティ操作
    '''

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
        '''
        JSON-LDのインスタンス変数を返す
        '''
        return self._jsonld

    def set_name(self, name):
        '''
        keyが"name"となるvalueをJSON-LDに追加する
        '''
        self._jsonld['name'] = name

    def add_properties(self, properties):
        '''
        JSON-LDに別のJSON-LDを合成する
        '''
        self._jsonld.update(properties)

    def get(self, property_name):
        '''
        JSON-LDの指定されたkeyに対応するvalueを返す
        '''
        return self._jsonld.get(property_name)

    def get_id_dict(self) -> dict:
        '''
        エンティティの@id key-valueを辞書で返す
        '''
        return {"@id":self.get("@id")}


class RootDataEntity(Entity):
    '''
    RootDataEntity用にEntityクラスを拡張
    @id, @typeを規定値にし、作成日時を追加
    '''

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
    '''
    Self-describing Entity用にEntityクラスを拡張
    @id, @typeを規定値にし、conformsTo, about keyを追加
    '''

    def __init__(self, id_=const.BASENAME, type_='CreativeWork'):
        super().__init__(id_, type_)

    def _empty(self):
        val = {"@id": self.id,
               "@type": self.type,
               "conformsTo": {"@id": const.PROFILE},
               "about": {"@id": "./"}}
        return val
