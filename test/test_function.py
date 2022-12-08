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

    @pytest.mark.parametrize('filepath',[
        '/test-data/not_existing_file.json',
        # 通らない絶対path, False
    ])
    @pytest.mark.parametrize(('func','exception'),[
        (generate.read_dmp, FileNotFoundError ),
        (main.generate_rocrate, SystemExit ),
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
    @pytest.fixture()
    def metadata(self, request):
        return generate.read_dmp(request.param)

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

    # dmp形式がエラー
    filepaths_1 = [
        '/app/test/test-data/test_error.json',
        '/app/test/test-data/test_nokey.json',
    ]

    @pytest.mark.parametrize('metadata', filepaths_1, indirect=['metadata'])
    def test_checking_dmp_error(self, metadata):
        '''
        dmpの形式抽出エラー
        - valueの値が規定値以外
        - keyがない
        '''
        with pytest.raises(generate.ValidationError):
            generate.check_dmp_format(metadata)


     # dmp形式以外がJSON-Schemaエラー
    filepaths_2 = [
        '/app/test/test-data/schema_errors/lack_required_01.json',
        '/app/test/test-data/schema_errors/lack_required_02.json',
        '/app/test/test-data/schema_errors/lack_required_03.json',
        '/app/test/test-data/schema_errors/lack_required_04.json',
        '/app/test/test-data/schema_errors/lack_required_05.json',
    ]
   
    @pytest.mark.parametrize('metadata', filepaths_2, indirect = ['metadata'] )
    def test_json_validation_error(self, metadata):
        '''
        JSON-schemaでvalidationエラー (dmpformat以外)
        - 必須項目がない (第一階層, 第二階層)
        - 必須項目があるが、型が不適当
        - オプション項目の型が不適当
        - 規定されていないkeyが存在する
        '''
        with pytest.raises(generate.ValidationError):
            generate.validate_with_schema(metadata)
        # - 必須項目がない (第一階層, 第二階層)
        # - 必須項目があるが、型が不適当 (dict, list含む)
        # - オプション項目の型が不適当
        # - 規定されていないkeyが存在する


    @pytest.mark.parametrize('filepath',filepaths_1 + filepaths_2)
    def test_errorcode(self, filepath):
        '''
        DMP形式抽出エラーもしくはJSON-schemaでvalidationエラー時に終了コードが1
        '''
        with pytest.raises(SystemExit):
            main.generate_rocrate(filepath)


class TestSetJSONbyScript:
    '''
    入力JSONをメソッド側でvalidation
    '''

    def test_checkbyscript_error(self):
        '''
        入力JSONをスクリプトでvalidationしエラー
        '''
        pass
        # 別エンティティでnameやURLに重複がある
        # 同一エンティティを指すがプロパティの値が異なっている
        # どちらか必須が欠けている


class TestSetDataEntity:
    '''
    データエンティティの生成
    '''

    def test_data_entity(self):
    # データエンティティ
    # ディレクトリを読まないときはJSONに入力必須, OK/エラー
    # JSONを読んだ時の分岐
        pass