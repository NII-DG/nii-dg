# NII-DG: Schema definition

## Schema の実体

1 つの schema 定義に関わるファイルとして 3 つのファイルが存在する

- Yaml file (e.g., [`../nii_dg/schema/base.yml`](../nii_dg/schema/base.yml))
- Python module (e.g., [`../nii_dg/schema/base.py`](../nii_dg/schema/base.py))
- Markdown file (e.g., [`./docs/base.md`](./docs/base.md))
- JSON-LD file (e.g., [`../context/base.jsonld`](../context/base.jsonld))

このうち、Markdown file、JSON-LD file は Yaml file から生成されるため、直接編集する必要はない。

### Yaml file

各 Entity の schema が記述される。例えば `File` Entity の場合、

```yaml
File:
  description: A file included in the research project, e.g. text file, script file and images.
  props:
    '@id':
      expected_type: str
      example: config/setting.txt
      required: Required.
      description: MUST be either a URI Path relative to RO-Crate root or an absolute URI from which is downloadable. When the file is from outside the repository, @id SHOULD be directly downloadable by a simple retrieval (e.g., HTTP GET), permitting redirections and HTTP/HTTPS authentication. RO-Crate itself (ro-crate-metadata.json) is excluded.
    name:
      expected_type: str
      example: setting.txt
      required: Required.
      description: Indicates the file name.
    contentSize:
      expected_type: str
      example: 1560B
      required: Required.
      description: MUST be an integer of the file size with the suffix `B` as a unit, bytes. If necessary, you can also use "KB", "MB", "GB", "TB" and "PB" as a unit.
    ...
```

であり、この例において、`File` Entity は `@id`, `name`, `contentSize` という 3 つの property を持つことが定義されている。

それぞれの property について、:

- `expected_type`
  - 期待されるデータ型
  - Python typing module の記述方に準拠する
    - そのため、`Dict[str, int]` のような記述が可能
    - 他の Entity を参照する場合は、`List[File]` のように記述する
    - 他の Entity の参照は、同一 schema 内の Entity のみ可能
      - ただし、後述する拡張 schema において、共通 schema からの参照は可能
- `example`
  - property の value の例
- `required`
  - その property が必須かどうかについて
  - 取りうる値として、`Required.`, `Optional.` がある
  - `Required when accessRights has Unshared or Restricted Closed Sharing.` といったように、特定の条件下で必須となる場合もある
  - そのため、`check_props` での検証では、完全一致で `Required.` を判定している
- `description`
  - property の説明
  - 自然言語での検証ルールがこの description に記述される

その他の注意点として、:

- 各 Entity は CamelCase で命名する
- `@id` props は全ての Entity において必須となる
- `@type` props の値は、各 Entity の命名が用いられるため、この schema 定義において、明示的に記述する必要はない
- `@id` は、URI で記述されることが推奨される

Yaml schema file 自体の検証と format のために、[`./scripts/validate_and_format_yml.py`](./scripts/validate_and_format_yml.py) が用意されている。

```bash
$ python3 validate_and_format_yml.py <source_yml> <dest_yml>
```

### Python module

各 Entity をそれぞれ Python Class として定義する。例えば、`File` Entity の場合、

```python
class File(DataEntity):
    def __init__(self, id_: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(id_=id_, props=props, schema_name=SCHEMA_NAME)

    def check_props(self) -> None:
        # Packaging で呼び出される各 props の型検査処理
        pass

    def validate(self, crate: "ROCrate") -> None:
        # Validation で呼び出されるより高度な検証処理
        pass
```

であり、`check_props()` と `validate()` をそれぞれ実装することで、各 Entity の検証ルールを定義することができる。

### Markdown file

Markdown file は、Yaml schema file から生成される閲覧用のドキュメントである。[`./scripts/generate_docs.py`](./scripts/generate_docs.py) を用いて Yaml schema file から生成される。

```bash
$ python3 generate_docs.py <source_yml> <dest_md>
```

## 現状定義されている Schema

Schema 定義として、

- 共通 schema
- DMP・分野・プラットフォーム別 schema (拡張 schema と呼ぶ)

の 2 種類に分けられる。

この内、共通 schema は、

- [`../nii_dg/schema/base.yml`](../nii_dg/schema/base.yml)
- [`../nii_dg/schema/base.py`](../nii_dg/schema/base.py)
- [`./docs/base.md`](./docs/base.md)

として定義されている。

拡張 schema は、[`../nii_dg/schema/amed.yml`](../nii_dg/schema/amed.yml) や [`../nii_dg/schema/amed.py`](../nii_dg/schema/amed.py) のように分野名を file 名の prefix として用いている。

現状定義されている拡張 schema として、

- `cao`
  - 内閣府「[公的資金による研究データの管理・利活用](https://www8.cao.go.jp/cstp/kenkyudx.html)に関する基本的な考え方」におけるメタデータの共通項目
  - [参考 docs](https://www8.cao.go.jp/cstp/common_metadata_elements.pdf)
- `amed`
  - 日本医療研究開発機構
  - [参考 Web Page](https://www.amed.go.jp/koubo/datamanagement.html)
- `meti`
  - 経済産業省
  - [参考 Web Page](https://www.meti.go.jp/policy/innovation_policy/datamanagement.html)
  - 新エネルギー・産業技術総合開発機構 (NEDO)、生物系特定産業技術研究支援センター (BRAIN) はこれを選択
- `ginfork`
  - ginfork 用の拡張 schema

が挙げられる。

## Schema の追加と拡張

- 基本的に共通 schema の追加と拡張は想定されていない
  - 多くの `File` や `Person` といった基本的な Entity は、共通 Schema において定義されている
  - そのため、`amed:DMPMetadata:creator` の値として、共通 schema の `base:Person` Entity を指定することが可能である
- 拡張 schema において、Entity を定義する場合は、上述の Yaml/Python/Markdown schema file を作成し、それぞれ記述する
  - 共通 schema に定義されていない Entity の場合
    - そのまま記述する
  - 共通 schema に定義されている Entity の場合
    - 想定としては、検証ルールを一部変更したり、新たな properties を追加することが考えられる
    - この場合、共通 schema の Entity を継承する
      - Yaml file: クリップボード的にコピペして、編集する
      - Python module:
      - `base.py` に定義されている Entity を継承し、`check_props()` と `validate()` を実装する
      - `__init__()`において継承する Entity は親ではなく、親の親を指定

## JSON-LD の生成

[`./scripts/generate_jsonld.py`](./scripts/generate_jsonld.py) を用いて、Yaml schema file から JSON-LD の context file を生成する。

```bash
$ python3 generate_jsonld.py <source_yml> <dest_jsonld>
```
