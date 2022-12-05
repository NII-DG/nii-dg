import pytest
from nii_dg.model.rocrate import ROCrate
from nii_dg import generate, main

@pytest.fixture
def metadata() -> dict:
    yield generate.read_dmp('/app/test/common_sample.json')

@pytest.mark.parametrize(('path', 'expected'),[
    ('./common_sample.json', True)
    # 通る絶対path, True
])
def test_reading_json_normal(path, expected):
    '''
    入力をdictとして読み込む
    '''
    assert isinstance(generate.read_dmp(path), dict) is expected

@pytest.mark.parametrize('path',[
    './not_existing_file.json'
    # 通らない絶対path, False
])
def test_reading_json_error(path):
    '''
    入力ファイルのパスが見つからない場合,エラー
    '''
    with pytest.raises(FileNotFoundError):
         main.generate_rocrate(path)


def test_setting_dmp_normal(metadata):
    '''
    dmpの形式を抽出する
    '''
    pass
    # common, JST, AMED, METI

def test_setting_dmp_error(metadata):
    '''
    dmpの形式を抽出する
    '''
    pass
    # dmpがcommon, JST, AMED, METI以外
    # dmpのkeyがない


def test_jsonschema_normal():
    '''
    入力JSONをJSON-Schemaに通す
    '''
    pass
    # dmpが正しい

def test_jsonschema_normal():
    '''
    入力JSONをJSON-Schemaに通す
    '''
    pass
    # dmpが該当していない
    # dmpのkeyがない
