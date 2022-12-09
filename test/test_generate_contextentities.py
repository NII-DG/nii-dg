'''
入力JSONからコンテキストエンティティ生成
'''

import pytest
from nii_dg.model.rocrate import NIIROCrate
from nii_dg import generate, main


def test_checkbyscript_normal(self):
    '''
    入力JSONからコンテキストエンティティを正常に生成
    '''
    pass
    # エンティティが正しく生成される
    # RO-Crateが正しく生成される


def test_checkbyscript_error(self):
    '''
    入力JSONに対して生成時にエラー
    '''
    pass
    # エンティティ単位で「いずれか必須」全てが欠けている
    # 同種のエンティティ：同一エンティティを指すがプロパティの値が異なっている
    # 別エンティティでnameやURLに重複がある

def test_errorcode(self):
    '''
    生成エラー時に終了コードが1
    '''
    # with pytest.raises(SystemExit):
    #     main.generate_rocrate(filepath)
    pass