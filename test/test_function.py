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
        入力をdictとして読み込む, 正常系
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
    @pytest.mark.parametrize('filepath', [
        '/app/test/test-data/test_common.json',
        '/app/test/test-data/test_JST.json',
        '/app/test/test-data/test_AMED.json',
        '/app/test/test-data/test_METI.json',
    ])
    def test_setting_dmp_normal(self, filepath):
        '''
        dmpの形式を抽出する, 正常系
        - common metadata, JST, AMED, METIのいずれか
        '''
        metadata = generate.read_dmp(filepath)
        assert isinstance(generate.set_dmp_format(metadata), NIIROCrate)
        # common, JST, AMED, METI

    @pytest.mark.parametrize('filepath', [
        './test-data/test_error.json',
        './test-data/test_nokey.json',
    ])
    def test_setting_dmp_error(self, filepath):
        '''
        dmpの形式を抽出する
        - valueの値が規定値以外
        - keyがない
        '''
        metadata_error = generate.read_dmp(filepath)
        with pytest.raises(generate.ValidationError):
            generate.set_dmp_format(metadata_error)


def test_jsonschema_normal():
    '''
    入力JSONをJSON-Schemaでvalidation
    '''
    pass
    # dmp-jsonの必須項目が埋まっている (minimum)
    # 必須項目+オプション全部乗せ (Maximum)

def test_jsonschema_error():
    '''
    入力JSONをJSON-Schemaでvalidation, 異常系
    '''
    pass
    # 必須項目がない
    # 規定外のプロパティがある
    # valueの型が違う
        # dictがdictでない
        # listがlistでない
    # 別エンティティでnameやURLに重複がある
    # どちらか必須が欠けている

# データエンティティ
# ディレクトリを読まないときはJSONに入力必須, OK/エラー
# JSONを読んだ時の分岐