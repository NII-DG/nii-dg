import pytest
from nii_dg.model.rocrate import NIIROCrate
from nii_dg import generate, main


class TestReadJson:
    '''
    JSON読み込み
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
        # 通らない相対path, False
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
        '''
        metadata = generate.read_dmp(filepath)
        assert isinstance(generate.generate_crate_instance(metadata), NIIROCrate)

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
        '/app/test/test-data/schema_errors/lack_required_level1.json', # 第一階層の必須項目がない
        '/app/test/test-data/schema_errors/lack_required_level2.json', # 第二階層の必須項目がない
        # 必須項目があるが、型が不適当
        # オプション項目の型が不適当
        # 規定されていないkeyが存在する
    ]
   
    @pytest.mark.parametrize('metadata', filepaths_2, indirect = ['metadata'] )
    def test_json_validation_error(self, metadata):
        '''
        JSON-schemaでvalidationエラー (dmpformat以外)
        '''
        with pytest.raises(generate.ValidationError):
            generate.validate_with_schema(metadata)


    @pytest.mark.parametrize('filepath',filepaths_1 + filepaths_2)
    def test_errorcode(self, filepath):
        '''
        DMP形式抽出エラーもしくはJSON-schemaでvalidationエラー時に終了コードが1
        '''
        with pytest.raises(SystemExit):
            main.generate_rocrate(filepath)


class TestSetJSONbyScript:
    '''
    入力JSONからコンテキストエンティティ生成
    '''
    def test_checkbyscript_normal(self):
        '''
        入力JSONからコンテキストエンティティを正常に生成
        '''
        pass
        # エンティティが正しく生成される
        # RO-Crateが正しく生成される


    def test_checkbyscript_error(self):
        '''
        入力JSONに対してvalidationエラー
        '''
        pass
        # エンティティ単位で「いずれか必須」全てが欠けている
        # 同一エンティティを指すがプロパティの値が異なっている
        # 別エンティティでnameやURLに重複がある

    def test_errorcode(self):
        '''
        入力JSONのvalidationしエラー時に終了コードが1
        '''
        # with pytest.raises(SystemExit):
        #     main.generate_rocrate(filepath)
        pass


class TestSetDataEntity:
    '''
    データエンティティの生成
    '''

    def test_data_entity(self):
    # JSON-Schemaベースのvalidationは既にクリア
    # JSONから生成, OK
        pass

    def test_data_entity_error(self):
    # JSON-Schemaベースのvalidationは既にクリア
    # JSONから生成, エラー
    # ディレクトリなのに@idが/で終わっていない、など
        pass

    def test_load_data_dir(self):
        #指定ディレクトリを読み込みエンティティ生成
        pass

    def test_load_data_dir_error(self):
        #指定ディレクトリを読み込みエンティティ生成,エラー
        # 指定ディレクトリがない
        # 指定ディレクトリが空
        pass

class TestGenerateRocrate:
    '''
    JSON-LDとしてro-crate-metadata.jsonの生成
    '''
    def test_generate_rocrate(self):
        # 正常系、終了コードが0
        # main.generate_rocrate(json)
        pass

    def test_generate_rocrate_error(self):
        # 生成時エラー、終了コードが1
        # main.generate_rocrate(json)
        pass