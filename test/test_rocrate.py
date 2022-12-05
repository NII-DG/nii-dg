import pytest
from nii_dg.model.rocrate import ROCrate
from nii_dg.model.entities import Entity

@pytest.fixture(scope="module")
def crate() -> ROCrate:
    yield ROCrate()

def test_get_by_type(crate):
    assert len(crate.get_by_type("Dataset")) == 1
    assert isinstance(crate.get_by_type("Dataset")[0], Entity)

def test_add_entity_01(crate):
    # create new entity
    assert crate.add_entity("id", "Type", {"name":"test"}) == {"@id":"id"}
    assert len(crate.entities) == 3
    assert crate.entities[2].get_jsonld() == {
        "@id":"id",
        "@type":"Type",
        "name":"test"
    }

def test_add_entity_02(crate):
    # if an entity already exists
    assert crate.add_entity("id", "Type", {"description":"update entity"}) == {"@id":"id"}
    assert len(crate.entities) == 3
    assert crate.entities[2].get_jsonld() == {
        "@id":"id",
        "@type":"Type",
        "name":"test",
        "description":"update entity"
    }

def test_get_by_name_01(crate):
    test_e = crate.get_by_name("test")
    assert isinstance(test_e, Entity)
    assert test_e.get("@id") == "id"

def test_get_by_name_02(crate):
    assert crate.get_by_name("notfound") == None

def test_get_by_id_01(crate):
    test_e = crate.get_by_id("id")
    assert isinstance(test_e, Entity)
    assert test_e.get("name") == "test"

def test_get_by_id_02(crate):
    assert crate.get_by_id("notfound") == None

@pytest.mark.parametrize(('namedict', 'expected'),[
    ({"name":"test"}, {"@id":"id"}),
    ({"name":"notfound"}, None),
])
def test_convert_name_to_id_01(crate, namedict, expected):
    assert crate.convert_name_to_id(namedict) == expected

def test_convert_name_to_id_02(crate):
    with pytest.raises(TypeError):
        crate.convert_name_to_id({"noname":"test"})
