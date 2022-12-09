'''
JSONファイルの読み込みテスト
'''
import pytest
from nii_dg import generate, main


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