#!/usr/bin/env python3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from nii_dg import const


class ValidationError(Exception):
    pass


class Entity():
    """
    エンティティ操作
    """

    def __init__(self, id_: str, type_: str) -> None:
        self.id = id_
        self.type = type_
        self._jsonld = self._empty()

    def _empty(self) -> Dict[str, str]:
        val = {
            "@id": self.id,
            "@type": self.type
        }
        return val

    def get_jsonld(self) -> Dict[str, str]:
        """
        JSON-LDのインスタンス変数を返す
        """
        return self._jsonld

    def set_id(self, id_: str) -> None:
        """
        keyが"@id"となるvalueをJSON-LDに追加もしくは上書きする
        """
        self._jsonld["@id"] = id_

    def set_name(self, name: str) -> None:
        """
        keyが"name"となるvalueをJSON-LDに追加する
        """
        self.get_jsonld()["name"] = name

    def add_properties(self, properties: Dict[str, str]) -> None:
        """
        JSON-LDに別のJSON-LDを合成する
        同じkeyに対して異なるvalueがある場合、エラー
        """
        for k, v in properties.items():
            if k not in self._jsonld:
                continue
            if v != self._jsonld[k]:
                raise ValidationError(f"Different values were found for the same key {k}")

        self._jsonld.update(properties)

    def get(self, property_name: str) -> Optional[str]:
        """
        JSON-LDの指定されたkeyに対応するvalueを返す
        """
        return self.get_jsonld().get(property_name)

    def get_id_dict(self) -> Dict[str, str]:
        """
        エンティティの@id key-valueを辞書で返す
        """
        if self.get("@id") is None:
            raise KeyError("This entity doesn't have @ id property.")
        return {"@id": self.get("@id")}


class RootDataEntity(Entity):
    """
    RootDataEntity用にEntityクラスを拡張
    @id, @typeを規定値にし、作成日時を追加
    """

    def __init__(self, id_: str = "./", type_: str = "Dataset") -> None:
        super().__init__(id_, type_)

    def _empty(self) -> Dict[str, str]:
        val = {
            "@id": self.id,
            "@type": self.type,
            "datePublished": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        }
        return val


class Metadata(Entity):
    """
    Self-describing Entity用にEntityクラスを拡張
    @id, @typeを規定値にし、conformsTo, about keyを追加
    """

    def __init__(self, id_: str = const.BASENAME, type_: str = "CreativeWork"):
        super().__init__(id_, type_)

    def _empty(self) -> Dict[str, Any]:
        val = {"@id": self.id,
               "@type": self.type,
               "conformsTo": {"@id": const.PROFILE},
               "about": {"@id": "./"}}
        return val
