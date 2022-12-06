import pytest
from nii_dg.model.rocrate import NIIROCrate
from nii_dg import generate, main


class TestReadJson:
    '''
    JSON読み込みのテスト
    '''

    @pytest.mark.parametrize('filepath',[
        './common_sample.json',
        # 通る絶対path
    ])
    def test_reading_json_normal(self, filepath):
        '''
        入力をdictとして読み込む, パスが通る
        '''
        assert isinstance(generate.read_dmp(filepath), dict)

    @pytest.mark.parametrize(('filepath', 'func','exception'),[
        ('./not_existing_file.json', generate.read_dmp, FileNotFoundError ),
        ('./not_existing_file.json', main.generate_rocrate, SystemExit ),
        # 通らない絶対path, False
    ])
    def test_reading_json_error(self, filepath, func, exception):
        '''
        入力をdictとして読み込む,パスが見つからない場合にエラー
        '''
        with pytest.raises(exception):
            func(filepath)

class TestSetDmp:
    '''
    dmpの形式抽出
    '''

    @pytest.fixture
    def metadata(self) -> dict:
        yield generate.read_dmp('/app/test/common_sample.json')

    def test_setting_dmp_normal(self, metadata):
        '''
        dmpの形式を抽出する
        '''
        assert isinstance(generate.set_dmp_format(metadata), NIIROCrate)
        # common, JST, AMED, METI

    @pytest.mark.parametrize(('filepath','exception'), [
        ('./test-data/test_error.json', FileNotFoundError),
        ('./test-data/test_nokey.json', generate.ValidationError),
    ])
    def test_setting_dmp_error(self, filepath, exception):
        '''
        dmpの形式を抽出する, 異常系
        - valueの値が規定値以外
        - keyがない
        '''
        metadata_error = generate.read_dmp(filepath)
        with pytest.raises(exception):
            generate.set_dmp_format(metadata_error)
        # dmpがcommon, JST, AMED, METI以外
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