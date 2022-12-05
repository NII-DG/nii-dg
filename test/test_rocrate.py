import pytest
from nii_dg.model.rocrate import ROCrate
from nii_dg.model.entities import Entity

@pytest.fixture
def crate() -> ROCrate:
    yield ROCrate()

def test_get_by_type(crate):
    assert len(crate.get_by_type("Dataset")) == 1
    assert isinstance(crate.get_by_type("Dataset")[0], Entity)

def test_add_entity(crate):
    # create new entity
    assert crate.add_entity("id", "Type", {"name":"test"}) == {"@id":"id"}
    assert len(crate.entities) == 3
    assert crate.entities[2].get_jsonld() == {
        "@id":"id",
        "@type":"Type",
        "name":"test"
    }
    # if an entity already exists
    assert crate.add_entity("id", "Type", {"description":"update entity"}) == {"@id":"id"}
    assert len(crate.entities) == 3
    assert crate.entities[2].get_jsonld() == {
        "@id":"id",
        "@type":"Type",
        "name":"test",
        "description":"update entity"
    }
