'''
データエンティティの生成
'''

import pytest

from nii_dg import generate, main
from nii_dg.model.rocrate import NIIROCrate


def test_data_entity() -> None:
    # JSON-Schemaベースのvalidationは既にクリア
    # JSONから生成, OK
    pass


def test_data_entity_error() -> None:
    # JSON-Schemaベースのvalidationは既にクリア
    # JSONから生成, エラー
    # ディレクトリなのに@idが/で終わっていない、など
    pass


def test_load_data_dir() -> None:
    # 指定ディレクトリを読み込みエンティティ生成
    pass


def test_load_data_dir_error() -> None:
    # 指定ディレクトリを読み込みエンティティ生成,エラー
    # 指定ディレクトリがない
    # 指定ディレクトリが空
    pass
