# NII-DG: NII Data Governance Library

データガバナンス: `データ管理に対して、組織として、明確な理念のもとに体制を構築し、具体的に実施するようにする`

を達成するため、本ライブラリは以下の機能を提供する。

- 研究データ (実データやメタデータ) の標準的なパッケージング (RO-Crate 化)
- 研究データの検証ルールの定義
- 研究データの検証

## Installation

Python 3.8 以上を推奨。

```bash
# Install from PyPI [TODO: not available yet]
$ pip install nii-dg

# Or install from source
$ git clone <this repo>
$ cd nii-dg
$ python3 -m pip install .
```

### Docker

Docker を用いた実行も可能。

```bash
$ docker build -t nii-dg .
$ docker run -it --rm -v $(pwd):/app nii-dg
```

## Usage

上記した通り、本ライブラリは 3 つの機能に分かれている。

1. Packaging: パッケージング (RO-Crate 化)
2. Rules: 検証ルールの定義
3. Validation: 検証

### Usage: 1. Packaging

研究データ (実データやメタデータ) のパッケージング、つまり RO-Crate 化を行う。
そのため、入力としては、研究データとそのメタデータ、出力としては RO-Crate (ro-crate-metadata.json) が生成される。

Packaging におけるインタフェースとして:

1. Python library
2. CLI

が用意されている。

#### Usage: 1.1. Packaging with Python library

Python library の使用例としては、以下のようになる。

```python
import nii_dg

# Generate RO-Crate object [TODO: update this example, now it's not working]
ro_crate = nii_dg.RO_Crate()

# Add file and author
file = nii_dg.File('path/to/file')
author = nii_dg.Author('John Doe', affiliation='NII')
file.created_by = author
ro_crate.add_file(file)
ro_crate.add_author(author)

# Generate RO-Crate metadata
ro_crate.dump('ro-crate-metadata.json')
```

また、後述 (at Usage: 1.2.) する JSON ファイルからの生成にも対応している。

```python
import nii_dg

# Generate RO-Crate object from JSON file
ro_crate = nii_dg.RO_Crate.from_json('path/to/input.json')
ro_crate.dump('ro-crate-metadata.json')
```

#### Usage: 1.2. Packaging with CLI

[TODO: そもそも CLI は必要か？]
[TODO: JSON からの生成って言っているけど、なんか二度手間感あるのでは？]

CLI では、JSON ファイルからの生成に対応している。

```bash
$ nii-dg package path/to/input.json
```

入力となる JSON ファイルの例としては、以下のようなものがある。

```json
{
  "title": "Sample RO-Crate",
  "author": [
    {
      "name": "John Doe",
      "affiliation": "NII"
    }
  ],
  "files": [
    {
      "path": "path/to/file",
      "created_by": "John Doe"
    }
  ]
}
```

これらの input.json には、研究メタデータの他、DMP(データマネジメントプラン)の情報が含まれている。

- DMP の形式
- プロジェクト名
- 研究資金提供機関
- リポジトリ
- データ作成者
- データ管理機関
- データ管理者
- DMP の記載内容

実際の仕様については、[詳細ドキュメント](https://github.com/ascade/nii-dg/blob/9d56cba94da139bf5ec23d5432d48dbafc9d6097/tests/README.md) を参照。
また、サンプルとして、[サンプル](https://github.com/ascade/nii-dg/blob/f0f76213d5365ab5ed43902028060a335b8edb34/tests/common_sample.json) を用意している。

### Usage: 2. Rules

検証ルールとして、

- 共通スキーマ: 全ての分野における検証ルール
- 分野別スキーマ: それぞれの分野における検証ルール and それぞれのプラットフォームごとの検証ルール

がある。

[TODO: Rule 一覧取得]

### Usage: 3. Validation

[TODO: not written yet]

- with Python library
  - `nii-dg.validate(path/to/ro-crate-metadata.json)`
  - `nii-dg.validate(path/to/ro-crate-metadata.json, rules=<json|string?>)`
- with CLI
  - `nii-dg validate path/to/ro-crate-metadata.json`
  - `nii-dg validate --rules <json|string?> path/to/ro-crate-metadata.json`
- with REST API
  - `POST /validate { "ro_crate": <json|string?>, "rules": <json|string?> }`
  - [TODO: write about authentication]

## Development

[TODO: write for docker development environment]
[TODO: write about linting, testing, etc.]

### Testing

[TODO: Unit test]
[TODO: Integration test for CLI, REST API]

## License

[TODO: not set yet]
