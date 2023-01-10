# NII-DGライブラリによるパッケージング (RO-Crate生成) の実行例

## Installation

Python (version>=3.8) を利用する。

```
$ python3 -m pip install .
```

### Docker

Dockerを利用する場合は、例えば以下のように環境を用意する。

```
$ docker run -ti -v $PWD:/app python3-slim bash

# in container
$ cd /app; python3 -m pip install .
```

## サンプル実装の実行

```
$ python3 tests/example.py
```

`tests/example.py` のパッケージングの実装例では、以下のような RO-Crate が生成される。

```
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    {
      "@id": "./",
      "@type": "Dataset",
      "hasPart": [
        {
          "@id": "./data/file_1.txt"
        },
        {
          "@id": "./data/"
        }
      ],
      "name": "example research project",
      "funder": [
        {
          "@id": "https://www.nii.ac.jp/"
        }
      ],
      "dateCreated": "2023-01-10T07:19:23.632+00:00",
      "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/RootDataEntity.json"
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
    },
    {
      "@id": "./data/file_1.txt",
      "@type": "File",
      "name": "Sample File",
      "contentSize": "156GB",
      "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/File.json"
    },
    {
      "@id": "./data/",
      "@type": "Dataset",
      "name": "Sample Folder",
      "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Dataset.json"
    },
    {
      "@id": "https://www.nii.ac.jp/",
      "@type": "Organization",
      "name": "National Institute of Informatics",
      "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Organization.json"
    }
  ]
}
```

## 仕様

### RootDataEntityの生成
ROCrateインスタンスを生成すると、`root`としてRootDataEntityが生成される。

```python
from nii_dg.ro_crate import ROCrate

ro_crate = ROCrate()
ro_crate.root["name"] = "example research project"
```

### エンティティ生成
生成したいエンティティをimportし、インスタンス生成。プロパティの追加は第二引数(@idが固定のエンティティでは第一引数)の設定でも可能。
```python
from nii_dg.schema.base import Organization

funder = Organization("https://www.nii.ac.jp/", {"name": "National Institute of Informatics"})
```

### RO-Crateへエンティティ追加
生成したエンティティはaddメソッドでROCrateインスタンスに追加が必要。
```python
ro_crate.add(funder)
```

### JSON-LDに変換
as_jsonld()メソッドは戻り値としてROCrateインスタンスのJSON-LD形式の辞書を返す。
```python
json.dumps(ro_crate.as_jsonld())
```