# 検証
TBU
# RO-Crate生成ライブラリ
nii_dg
## 利用方法
### 入力ファイルの準備
メタデータ情報をもつJSONファイル(もしくはYAML)を作成する。詳細はdocument(準備中)を参照のこと。

### RO-Crate生成 
JSONファイルに対象データ情報が含まれる場合、それを引数に指定する。現在のディレクトリに`ro-crate-metadata.json`が生成される。
```python
from nii_dg import generate_rocrate

generate_rocrate('path/to/input.json')
```

対象データ情報をローカルから読み込む場合、そのディレクトリパスを第二引数に置く。同様に`ro-crate-metadata.json`が生成される。
```python
from nii_dg import generate_rocrate

generate_rocrate('path/to/input.json', 'path/to/dir')
```