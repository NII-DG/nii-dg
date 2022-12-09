'''
JSONからdmpの形式抽出
全DMP共通の項目をJSON schemaでvalidation (dmpformat以外)
'''
import pytest
from nii_dg.model.rocrate import NIIROCrate
from nii_dg import generate, main

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