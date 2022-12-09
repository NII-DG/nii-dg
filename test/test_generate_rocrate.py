'''
JSON-LDとしてro-crate-metadata.jsonの生成
'''

import pytest
from nii_dg.model.rocrate import NIIROCrate
from nii_dg import generate, main


def test_generate_rocrate():
    # 正常系、終了コードが0
    # main.generate_rocrate(json)
    pass

def test_generate_rocrate_error():
    # 生成時エラー、終了コードが1
    # main.generate_rocrate(json)
    pass