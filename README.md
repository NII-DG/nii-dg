# 検証

TBU

NII ガバナンス用スキーマに沿った RO-Crate を用意し、検証ルールを指定する?

# RO-Crate 生成ライブラリ

NII ガバナンス用スキーマに沿った RO-Crate を JSON から生成するためのライブラリ

## 利用方法

### 入力ファイルの準備

メタデータ情報をもつ JSON ファイル(もしくは YAML)を作成する。[サンプル](https://github.com/ascade/nii-dg/blob/f0f76213d5365ab5ed43902028060a335b8edb34/test/common_sample.json)

内容には研究メタデータの他、DMP(データマネジメントプラン)の情報を含む。

```
・DMPの形式
・プロジェクト名
・研究資金提供機関
・リポジトリ
・データ作成者
・データ管理機関
・データ管理者
・DMPの記載内容
等
```

[詳細ドキュメント](https://github.com/ascade/nii-dg/blob/9d56cba94da139bf5ec23d5432d48dbafc9d6097/test/README.md)

### RO-Crate 生成

JSON ファイルに対象データ情報が含まれる場合、それを引数に指定する。現在のディレクトリに`ro-crate-metadata.json`が生成される。

```python
import nii_dg

nii_dg.generate_rocrate('path/to/input.json')
```

対象データ情報をローカルから読み込む場合、そのディレクトリパスを第二引数に置く。同様に`ro-crate-metadata.json`が生成される。

```python
import nii_dg

nii_dg.generate_rocrate('path/to/input.json', 'path/to/dir')
```
