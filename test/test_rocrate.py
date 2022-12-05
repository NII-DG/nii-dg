import pytest
from nii_dg.model.rocrate import ROCrate
from nii_dg.model.entities import Entity

@pytest.fixture(scope="module")
def crate() -> ROCrate:
    '''
    RO-Crateクラスのインスタンス
    '''
    yield ROCrate()

def test_get_by_type_01(crate):
    '''
    該当するエンティティが存在する場合、それらのリストを返す
    '''
    assert len(crate.get_by_type("Dataset")) == 1
    assert isinstance(crate.get_by_type("Dataset")[0], Entity)

def test_get_by_type_02(crate):
    '''
    該当するエンティティが存在しない場合、空のリストを返す
    '''
    assert len(crate.get_by_type("Test")) == 0


def test_add_entity_01(crate):
    '''
    @idが同一のエンティティが存在しない場合、エンティティを新規作成
    '''
    assert crate.add_entity("id", "Type", {"name":"test"}) == {"@id":"id"}
    assert len(crate.entities) == 3 #初期化時点で2
    assert crate.entities[2].get_jsonld() == {
        "@id":"id",
        "@type":"Type",
        "name":"test"
    }

def test_add_entity_02(crate):
    '''
    @idが同一のエンティティがすでに存在する場合、そのエンティティにkey-valueをupdate
    '''
    assert crate.add_entity("id", "Type", {"description":"update entity"}) == {"@id":"id"}
    assert len(crate.entities) == 3 #初期化時点で2
    assert crate.entities[2].get_jsonld() == {
        "@id":"id",
        "@type":"Type",
        "name":"test",
        "description":"update entity"
    }

def test_get_by_name_01(crate):
    '''
    nameでエンティティを検索し、一致するエンティティを返す
    '''
    test_e = crate.get_by_name("test")
    assert isinstance(test_e, Entity)
    assert test_e.get("@id") == "id"

def test_get_by_name_02(crate):
    '''
    nameでエンティティを検索し、一致するエンティティがない場合はNoneを返す
    '''
    assert crate.get_by_name("notfound") is None

def test_get_by_id_01(crate):
    '''
    @idでエンティティを検索し、一致するエンティティを返す
    '''
    test_e = crate.get_by_id("id")
    assert isinstance(test_e, Entity)
    assert test_e.get("name") == "test"

def test_get_by_id_02(crate):
    '''
    @idでエンティティを検索し、一致するエンティティがない場合はNoneを返す
    '''
    assert crate.get_by_id("notfound") is None

@pytest.mark.parametrize(('namedict', 'expected'),[
    ({"name":"test"}, {"@id":"id"}),
    ({"name":"notfound"}, None),
])
def test_convert_name_to_id_01(crate, namedict, expected):
    '''
    keyが"name"のvalueで、エンティティのnameを検索し、一致するエンティティの@idのkey-valueを返す
    一致するエンティティがない場合はNoneを返す
    '''
    assert crate.convert_name_to_id(namedict) == expected

def test_convert_name_to_id_02(crate):
    '''
    引数にkey"name"がない場合はTypeErrorをraiseする
    '''
    with pytest.raises(TypeError):
        crate.convert_name_to_id({"noname":"test"})
