import pytest
from nii_dg.model.rocrate import NIIROCrate
from nii_dg import generate, main


class TestReadJson:
    '''
    JSON読み込みのテスト
    '''

    @pytest.mark.parametrize('path',[
        './common_sample.json',
        # 通る絶対path
    ])
    def test_reading_json_normal(self, path):
        '''
        入力をdictとして読み込む, パスが通る
        '''
        assert isinstance(generate.read_dmp(path), dict)

    @pytest.mark.parametrize(('func','exception','path'),[
        (generate.read_dmp, FileNotFoundError, './not_existing_file.json'),
        (main.generate_rocrate, SystemExit, './not_existing_file.json'),
        # 通らない絶対path, False
    ])
    def test_reading_json_error(self, func, exception, path):
        '''
        入力をdictとして読み込む,パスが見つからない場合にエラー
        '''
        with pytest.raises(exception):
            func(path)


@pytest.fixture
def metadata() -> dict:
    yield generate.read_dmp('/app/test/common_sample.json')

def test_setting_dmp_normal(metadata):
    '''
    dmpの形式を抽出する
    '''
    assert isinstance(generate.set_dmp_format(metadata), NIIROCrate)
    # common, JST, AMED, METI

@pytest.fixture
def metadata_error() -> dict:
    yield generate.read_dmp('./test-data/test_error.json')
def test_setting_dmp_error(metadata_error):
    '''
    dmpの形式を抽出する, 異常系
    '''
    with pytest.raises(FileNotFoundError):
        generate.set_dmp_format(metadata_error)
    # dmpがcommon, JST, AMED, METI以外

@pytest.fixture
def metadata_error2() -> dict:
    yield generate.read_dmp('./test-data/test_nokey.json')
def test_setting_dmp_error2(metadata_error2):
    '''
    dmpの形式を抽出する, 異常系
    '''
    with pytest.raises(generate.ValidationError):
        generate.set_dmp_format(metadata_error2)
    # dmpのkeyがない

def test_jsonschema_normal():
    '''
    入力JSONをJSON-Schemaに通す
    '''
    pass
    # dmpが正しい

def test_jsonschema_error():
    '''
    入力JSONをJSON-Schemaに通す
    '''
    pass
    # dmpが該当していない
    # dmpのkeyがない

def test_jsonschema_01():
    '''
    必須項目がない
    あるが、型が違う 
    別エンティティでnameやURLに重複がある
    '''
    pass

def test_jsonschema_02():
    '''
    必須以外のあるなしで分岐 
    '''
    pass

def test_filepath():
    print(__file__)