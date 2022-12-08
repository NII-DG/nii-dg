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
        ('/test-data/not_existing_file.json', generate.read_dmp, FileNotFoundError ),
        ('/test-data/not_existing_file.json', main.generate_rocrate, SystemExit ),
        # 通らない絶対path, False
    ])
    def test_reading_json_error(self, filepath, func, exception):
        '''
        入力をdictとして読み込む,パスが見つからない場合にエラー
        '''
        with pytest.raises(exception):
            func(filepath)


class TestSetJSON:
    '''
    JSONからdmpの形式抽出
    全DMP共通の項目をJSON schemaでvalidation (dmpformat以外)
    '''

    @pytest.mark.parametrize('filepath', [
        '/app/test/test-data/test_common.json',
        '/app/test/test-data/test_JST.json',
        '/app/test/test-data/test_AMED.json',
        '/app/test/test-data/test_METI.json',
        '/app/test/test-data/test_minimum_for_schema.json',
        '/app/test/test-data/test_maximum_for_schema.json',
    ])
    def test_generateing_normal(self, filepath):
        '''
        dmpの形式を抽出しJSON schemaでvalidation, 正常系
        - common metadata, JST, AMED, METIのいずれか
        - 必須項目が存在し、型が正しい
        - オプション項目が存在し、型が正しい
        - 規定されていないkeyが存在しない
        '''
        metadata = generate.read_dmp(filepath)
        assert isinstance(generate.generate_crate_instance(metadata), NIIROCrate)
        # common, JST, AMED, METI

    @pytest.mark.parametrize('filepath', [
        '/app/test/test-data/test_error.json',
        '/app/test/test-data/test_nokey.json',
    ])
    def test_checking_dmp_error(self, filepath):
        '''
        dmpの形式を抽出する
        - valueの値が規定値以外
        - keyがない
        '''
        metadata_error = generate.read_dmp(filepath)
        with pytest.raises(generate.ValidationError):
            generate.check_dmp_format(metadata_error)

    @pytest.mark.parametrize('filepath', [
        '/app/test/test-data/schema_errors/lack_required_01.json',
        '/app/test/test-data/schema_errors/lack_required_02.json',
        '/app/test/test-data/schema_errors/lack_required_03.json',
    ])
    def test_json_validation_error(self, filepath):
        '''
        JSON-schemaでvalidation (dmpformat以外)
        - 必須項目がない (第一階層, 第二階層)
        - 必須項目があるが、型が不適当
        - オプション項目の型が不適当
        - 規定されていないkeyが存在する
        '''
        metadata_error = generate.read_dmp(filepath)
        with pytest.raises(generate.ValidationError):
            generate.validate_with_schema(metadata_error)
        # - 必須項目がない (第一階層, 第二階層)
        # - 必須項目があるが、型が不適当
        # - オプション項目の型が不適当
        # - 規定されていないkeyが存在する

def test_jsonschema_normal():
    '''
    入力JSONをJSON-Schemaでvalidation, 正常系
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