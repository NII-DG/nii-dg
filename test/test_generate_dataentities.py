'''
データエンティティの生成
'''

import pytest
from nii_dg.model.rocrate import NIIROCrate
from nii_dg import generate, main


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