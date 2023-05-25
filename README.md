# NII-DG: NII Data Governance Library

[![flake8](https://github.com/NII-DG/nii-dg/actions/workflows/flake8.yml/badge.svg?branch=main&event=push)](https://github.com/NII-DG/nii-dg/actions/workflows/flake8.yml)
[![isort](https://github.com/NII-DG/nii-dg/actions/workflows/isort.yml/badge.svg?branch=main&event=push)](https://github.com/NII-DG/nii-dg/actions/workflows/isort.yml)
[![mypy](https://github.com/NII-DG/nii-dg/actions/workflows/mypy.yml/badge.svg?branch=main&event=push)](https://github.com/NII-DG/nii-dg/actions/workflows/mypy.yml)
[![pytest](https://github.com/NII-DG/nii-dg/actions/workflows/pytest.yml/badge.svg?branch=main&event=push)](https://github.com/NII-DG/nii-dg/actions/workflows/pytest.yml)

データガバナンス: `データ管理に対して、組織として、明確な理念のもとに体制を構築し、具体的に実施するようにする`

を達成するため、本ライブラリは以下の機能を提供する。

- 研究データ管理のための Metadata Schema とその検証ルールの定義
- 研究データのパッケージング (RO-Crate 化)
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
$ docker run -it --rm ghcr.io/NII-DG/nii-dg:latest bash
```

## Usage

上記の通り、本ライブラリは 3 つの機能に分かれている。

1. Schema definition: Metadata Schema とその検証ルールの定義
2. Packaging: パッケージング (RO-Crate 化)
3. Validation: 検証

![System architecture](https://user-images.githubusercontent.com/26019402/215007490-6f7b10b1-4e0d-4286-b7c6-6882a9c32948.png)

### Usage: 1. Schema definition

Document として [./schema/README.md](./schema/README.md) を参照。

### Usage: 2. Packaging

研究データ (実データやメタデータ) のパッケージング、つまり RO-Crate 化を行う。
そのため、入力としては、研究データとそのメタデータ、出力としては RO-Crate (ro-crate-metadata.json) を生成する。

Packaging には、Python library `nii_dg` を用いる。

Minimal example:

```python
from nii_dg.ro_crate import ROCrate

ro_crate = ROCrate()
ro_crate.root["name"] = "Sample RO-Crate"
ro_crate.dump("ro-crate-metadata.json")
```

出力として:

```json
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    {
      "@id": "./",
      "@type": "Dataset",
      "hasPart": [],
      "name": "Sample RO-Crate",
      "datePublished": "2023-01-27T04:16:02.470+00:00"
    },
    {
      "@id": "ro-crate-metadata.json",
      "@type": "CreativeWork",
      "conformsTo": {
        "@id": "https://w3id.org/ro/crate/1.1"
      },
      "about": {
        "@id": "./"
      }
    }
  ]
}
```

より詳細な説明として、以下の項目を参照。

また、使用例として、以下が用意されている。

- [./tests/example/example.py](./tests/example/example.py)

#### RO-Crate Metadata File Descriptor と Root Data Entity

上述の Minimal example における 2 つの Entity は、RO-Crate における [必須のエンティティ](https://www.researchobject.org/ro-crate/1.1/root-data-entity.html) である。
以下の 2 つが必須のエンティティである:

- RO-Crate Metadata File Descriptor
  - `@type`: `CreativeWork`
  - > The RO-Crate JSON-LD MUST contain a self-describing RO-Crate Metadata File Descriptor with the @id value ro-crate-metadata.json (or ro-crate-metadata.jsonld in legacy crates) and @type CreativeWork.
  - Called as `ROCrateMetadata` in this library.
  - RO-Crate metadata file に対する自己記述的な Entity
  - RO-Crate 自体の様々な metadata が記述される
- Root Data Entity
  - `@type`: `Dataset`
  - > This descriptor MUST have an about property referencing the Root Data Entity, which SHOULD have an @id of ./.
  - Called as `RootDataEntity` in this library.
  - RO-Crate が持つ file を取りまとめる Entity
  - Data Entity (e.g., `File`, `Dataset`) が `hasPart` として自動的に追加される

この 2 つの Entity は、`ROCrate` インスタンスの生成時に自動的に生成される。`ROCrate.root` により、`RootDataEntity` に対応する Entity にアクセスできる。

#### 各 Entity の作成と RO-Crate への追加

Entity は、各 Entity クラスを用いて生成する。

```python
from nii_dg.schema.base import File
from nii_dg.schema.base import Organization

file = File("https://example.com/path/to/file", props={"name": "Example file"})
organization = Organization("https://example.com/path/to/organization", props={"name": "Example organization"})

# 生成後、Entity を ROCrate に追加する
from nii_dg.ro_crate import ROCrate
crate = ROCrate()
crate.add(file, organization)
```

これらの Entity クラスにおいて、第一引数として `@id` が渡される。また、`props` として、Entity に対する metadata が渡される。

これらの `props` は、Python class の `__set__` として、設定することも可能である。

```python
file["name"] = "Example file"
organization["name"] = "Example organization"

# entity を set する場合、`@id` として set される
crate.root["funder"] = [organization]

# -> {"funder": [{"@id": "https://example.com/path/to/organization"}]}
```

`base` 以外の schema の Entity においても、同様の操作が可能である。

```python
from nii_dg.schema.amed import File as AmedFile
amed_file = AmedFile("https://example.com/path/to/file", props={"name": "Example amed file"})
```

#### Entity における同一 `@id` の取り扱い

複数の schema を利用する場合、同一の `@id` を持つ Entity が存在する可能性がある。
これらの Entity は、JSON-LD における別ノードとして扱われるが、内部的には別 `@context` を持つため、別々の Entity として扱われる。

```python
from nii_dg.schame.amed import File as AmedFile
from nii_dg.schema.ginfork import File as GinforkFile

amed_file = AmedFile("path/to/file.txt", props={"name": "Example amed file"})
ginfork_file = GinforkFile("path/to/file.txt", props={"name": "Example ginfork file"})
```

この場合、JSON-LD において、

```json
{
  ...,
  "@graph": [
    {
      "@id": "path/to/file.txt",
      "@context": "https://example.com/path/to/context/amed.jsonld",
      "name": "Example amed file"
    },
    {
      "@id": "path/to/file.txt",
      "@context": "https://example.com/path/to/context/ginfork.jsonld",
      "name": "Example ginfork file"
    }
  ]
}
```

のように表現される。metadata の properties などは、`@context` により別の prop として扱われるため (e.g., `amed.File:name`, `ginfork.File:name`)、同一の `@id` が存在しても、それぞれ別の metadata が保持される。

#### Entity 単位での型検査と property の検証

本ライブラリでは、JSON-LD 生成時に (`ROCrate.dump`)、Entity が持つ各 prop の型検査が行われる。
この処理は、別途 `entity.check_props()` として、Entity 単位で行うことも可能である。

### Usage: 3. Validation

Validation として、`ROCrate.validate()` が用意されている。

```python
import json
from nii_dg.ro_crate import ROCrate

with open("path/to/ro-crate-matadata.json") as f:
    jsonld = json.load(f)
crate = ROCrate(jsonld=jsonld)
crate.validate()
```

仕様として、:

- この処理は、各 Entity の `entity.validate()` 処理を呼び出すことにより、行われる
  - Validation rule は、自然言語では各 schema file (YAML file) にて、実際の処理としては `entity.validate()` にて、定義されている
- Validation 処理は、最終的に各 entity の結果を取りまとめた後、まとめて結果が表示される

Packaging における型検査 (`entity.check_props()`) と、Validation における検証 (`entity.validate()`) は、基本的に異なる処理である。それぞれの処理の違いとして、:

- `entity.check_props()`:
  - 各 prop の型検査を行う
    - 例: 型定義 str に対して int が設定されているなど、型の不一致を検出する
  - required の prop が設定されているか、などの検査を行う
- `entity.validate()`:
  - より高度な検証を行う
  - 各 prop の「値」が正しいかを検証する
  - 複数の Entity 間の relation を用いてこれらの値の検証を行う

#### Using REST API Server

REST API の仕様として、[open-api_spec.yml](./open-api_spec.yml) を参照。

また、API Server の起動・実行に関して、[api-quick-start.md](./api-quick-start.md) を参照。

## JSON-LD Context を用いた schema の外部参照

本ライブラリは、ライブラリに含まれる YAML schema (e.g., [`nii_dg/schema/base.yml`](./nii_dg/schema/base.yml))と Python module (e.g., [`nii_dg/schema/base.py`](./nii_dg/schema/base.yml)) を用いて、研究データのパッケージと検証が行われる。
検証における入力は RO-Crate であるが、パッケージ時と検証時のライブラリバージョンが異なる場合、schema や検証ルールが異なる状態での検証が行われる可能性がある。
この問題を解決するため、JSON-LD の `@context` property を用いて、schema (i.e., yaml schema and python module) の外部参照を行う。

例として、[`nii_dg/schema/base.yml`](./nii_dg/schema/base.yml) と [`nii_dg/schema/base.py`](./nii_dg/schema/base.yml) を用いると、生成される `File` entity は以下のようになる。

```json
{
  "@id": "file_1.txt",
  "@type": "File",
  "@context": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/base.jsonld",
  "name": "Sample File",
  "contentSize": "128GB",
},
```

ここで、`@context` property により、`https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/schema/context/base.jsonld` にて、`File` entity の schema が定義されていることを示している。
更に、参照先の JSON-LD Context においては、下記のように定義されている。

```json
"File": {
  "@id": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File",
  "@context": {
    "@id": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:@id",
    "name": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:name",
    "contentSize": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:contentSize",
    "encodingFormat": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:encodingFormat",
    "sha256": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:sha256",
    "url": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:url",
    "sdDatePublished": "https://raw.githubusercontent.com/NII-DG/nii-dg/1.0.0/nii_dg/schema/base.yml#File:sdDatePublished"
  }
},
```

これにより、`File` entity 自体、及びその各 property について、schema の外部参照が行われることになる。

![System architecture extended](https://user-images.githubusercontent.com/26019402/228390256-5dcc5c81-3ba9-4be6-b0ab-1f6622c1fd2d.png)

実際の検証時には、RO-Crate 内の各 entity に記述されている `@context` を辿り、パッケージ時の Yaml schema と Python module を参照する。
ライブラリ内で、それらの file を読み込み、entity の instance を生成する。
その後、生成された entity の instance に含まれる schema や検証ルールを用いて、検証が行われる。

---

JSON-LD Context の生成については、[`./schema/REAMED.md`](./schema/REAMED.md) を参照。

また、JSON-LD の公開性がこの実装においては、重要な要素である。
そのため、本ライブラリでは、GitHub Actions により、JSON-LD Context の生成と公開を行っている。
GitHub Actions として、[`./.github/workflows/release.yml`](./.github/workflows/release.yml) が用意されている。

## Development

開発環境として Docker を利用する。

```bash
$ docker compose -f compose.dev.yml up -d --build
$ docker compose -f compose.dev.yml exec app bash

# in container
$ something you want to do
```

### Linter

Linter として、`flake8`, `isort`, `mypy` をそれぞれ用いている。

```bash
$ bash ./tests/lint_and_style_check/flake8.sh
$ bash ./tests/lint_and_style_check/isort.sh
$ bash ./tests/lint_and_style_check/mypy.sh

$ bash ./tests/lint_and_style_check/run_all.sh
```

また、それぞれの GitHub actions として、以下のように設定されている。

- [flake8](./.github/workflows/flake8.yml)
- [isort](./.github/workflows/isort.yml)
- [mypy](./.github/workflows/mypy.yml)

### Testing

`pytest` を用いた Unit Test が用意されている。

```bash
$ pytest -s ./tests/unit_test
```

また、GitHub actions として、以下のように設定されている。

- [pytest](./.github/workflows/pytest.yml)

### Documentation

`sphinx` を用いて、ドキュメントを生成する。

```bash
# 初期設定
$ sudo apt install python3-sphinx
$ sphinx-apidoc -F -H nii-dg -A NII -V 1.0.0 -o docs nii_dg

# ドキュメントの生成
$ sphinx-build ./docs ./docs/_build

# ドキュメントの確認
$ npx http-server ./docs/_build -a 0.0.0.0 -p 3000
```

## Branch and Release

Branch 管理として、

- `main`: Release の最新
  - main への直接の push は禁止とする
- `develop`: 開発用 branch
- `<other>`: それぞれの機能・修正用の branch
  - 基本的に、`develop` から `<other>` を切って開発を行い、`develop` にマージする

Release 作業として、`develop` から `main` への PR を作成し、マージする。
それぞれの Release は、`YYMMDD-<short_commit_hash>` という形式で tag が付与される。[TODO `setup.py` の version をどうするか]

Release 用の GitHub actions として、以下のように設定されている。

- [release](./.github/workflows/release.yml)

## License

[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
See the [LICENSE](https://github.com/sapporo-wes/yevis-cli/blob/main/LICENSE).
