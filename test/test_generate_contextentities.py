'''
入力JSONからコンテキストエンティティ生成
'''

import pytest

from nii_dg import generate, main
from nii_dg.model.rocrate import NIIROCrate


@pytest.fixture()
def crate(request) -> NIIROCrate:
    return generate.generate_crate_instance(generate.read_dmp(request.param))


@pytest.mark.parametrize("crate", ["/app/test/common_sample.json"], indirect=["crate"])
def test_checkbyscript_normal(crate: NIIROCrate) -> None:
    '''
    入力JSONからコンテキストエンティティを正常に生成
    '''
    generate.add_entities_to_crate(crate)
    assert len(crate.get_by_type("Person")) == 3
    assert len(crate.get_by_type("Organization")) == 3
    assert len(crate.get_by_type("RepositoryObject")) == 1
    assert len(crate.get_by_type("PropertyValue")) == 3

    # エンティティが正しく生成される


def test_checkbyscript_error() -> None:
    '''
    入力JSONに対して生成時にエラー
    '''
    pass
    # エンティティ単位で「いずれか必須」全てが欠けている
    # 同種のエンティティ：同一エンティティを指すがプロパティの値が異なっている
    # 別エンティティでnameやURLに重複がある


def test_errorcode() -> None:
    '''
    生成エラー時に終了コードが1
    '''
    # with pytest.raises(SystemExit):
    #     main.generate_rocrate(filepath)
    pass
