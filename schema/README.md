# NII-DG: Schema

## Memo

1. オレオレ json で common.json と amed.json を書く

https://github.com/ascade/nii-dg/schame/common.json

```json
{
  "File": {
    "name": {
      "desc": "foobar",
      "rule": "",
      "required": ""
    },
    "desc": {
      "desc": "foobar",
      "rule": "",
      "required": ""
    }
  },
  "Dataset": {
    "name": {
      "desc": "foobar",
      "rule": "",
      "required": ""
    },
    "desc": {
      "desc": "foobar",
      "rule": "",
      "required": ""
    }
  }
}
```

amed.json

```
{
    "File": {
        "name": {
            "desc": "foobar",
            "rule": "",
            "required": "False"
        },
        "size": {
            "desc": "foobar",
            "rule": "",
            "required": ""
        }
    }
}
```

2. オレオレ json から、md を生成 (自動生成)

3. context 用の json-ld を生成し、url として、オレオレ json を参照する (自動生成)

entity ごとに context.json file を自動生成する

### やりたいこと

生成した json ld の entity のなかの context に

https://github.com/ascade/nii-dg/schame/context.json/Common/File

とかいたら、

```
"File": "https://example.com/amed_file",
"name": "https://example.com/amed_file:name",
"desc": "https://example.com/amed_file:desc"
```

が帰ってくる

https://github.com/ascade/nii-dg/schema/context/common/file.json

[README] に context 以下はさわるなと書いておく

/schema/context/common/file.json

```json
{
    "@id": "https://w3id.org/ro/crate/1.1/context",
    "name": [
        "RO-Crate JSON-LD Context"
    ],
    "@context": {
        "File": "https://example.com/amed_file", -> <Github pages_url>#File
        "name": "https://example.com/amed_file:name", -> <Github pages_url>#File:name
        "desc": "https://example.com/amed_file:desc" -> <Github pages_url>#File:name
    }
}
```

## Directory 構造

- README.md
- scripts
  - generate_md.py
  - generate_rocrate_context.py
  - jsonschema
- amed.json
- base.json
- docs
  - amed.md
  - base.md
- context <- json-ld から呼ばれるためだけ (人間は触らない)
  - base
    - file.json
    - dataset.json
    - rootdatasetentity.json
    - ...
  - amed
    - file.json


## Memo

人が書くもの

- オレオレ json (schema 定義の json)
  - 2 パターン
    - common.json を継承するか？
    - common.json を cp するか？
- python file (schema 定義を反映した rule set / used by generator and validator)
  - 多分こっちの実装も上のパターンと同じにしたほうがなるべく良い

自動生成

markdown 仕様書
json ld context (referred by json ld (ro-crate))

## Extend とは

変更したいやつは base から cp してくる
追加したいやつは好きにかけ

---

common からの拡張の usecase

- field の追加
- field の削除
- field の変更
- entity の追加

---

このディレクトリには、NII-DG のスキーマ定義を記述する。
スキーマ定義は、

- 共通スキーマ
- 分野別スキーマ

に分けられる

## 共通スキーマ

[`common.md`](./common.md)

## 分野別スキーマ

- DMP ごと
- 研究分野ごと
- プラットフォームごと

といったそれぞれの環境ごとのスキーマ定義を記述する。

基本的には、共通スキーマを extend する形になる。(field の追加や検証ルールの追加)
もしくは、新たな Entity の追加

# NII-DG: Schema: Common

## 対象とした DMP 定義

- 内閣府「[公的資金による研究データの管理・利活用](https://www8.cao.go.jp/cstp/kenkyudx.html)に関する基本的な考え方」におけるメタデータの共通項目
  - 以下 `common metadata`とする
  - 参考: [PDF](https://www8.cao.go.jp/cstp/common_metadata_elements.pdf)
- 科学技術振興機構
  - 以下`JST`とする
  - 参考:[PDF](https://www.jst.go.jp/pr/intro/openscience/guideline_openscience_r4.pdf)
- 日本医療研究開発機構
  - 以下 `AMED`とする
  - 参考: [Web Page](https://www.amed.go.jp/koubo/datamanagement.html)
- 経済産業省
  - 以下`METI`とする
  - 参考:[Web Page](https://www.meti.go.jp/policy/innovation_policy/datamanagement.html)

## vocabulary

### dmpFormat

オリジナル語彙のため、語彙定義が必要

- common metadata
  - 2022/11 現在, GRDM で選択可能なものはこれのみ
- JST
- AMED
- METI
  - 新エネルギー・産業技術総合開発機構(NEDO),生物系特定産業技術研究支援センター(BRAIN)はこれを選択

### dmpDataNumber

オリジナル語彙のため、語彙定義が必要

### accessRights

- open access
- restricted access
- embargoed access
- metadata only access
- 参考: [JPCOAR スキーマガイドライン](https://schema.irdb.nii.ac.jp/ja/access_rights_vocabulary)

## Entity

### RootDataEntity

<table>
    <tr>
        <td>Property</td>
        <td>Required?</td>
        <td>Format and Rules</td>
        <td>Description</td>
        <td>Why needed</td>
    </tr>
    <tr>
        <th colspan="5">RootDataEntity</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>MUST end with <code>/</code> and SHOULD be the string <code>./</code></td>
        <td></td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>Dataset</i></td>
        <td></td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string<br>SHOULD identify the dataset to humans well enough to disambiguate it from other RO-Crates</td>
        <td>title of research project</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a><br>common
            metadata:3.プロジェクト名<br>AMED:研究開発課題名<br>METI:契約件名</td>
    </tr>
    <tr>
        <td>description</td>
        <td>MAY</td>
        <td>string<br>SHOULD further elaborate on the name to provide a summary of the context in which the dataset is
            important.</td>
        <td>description of research project</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a><br>Gakunin
            RDM:プロジェクトの説明</td>
    </tr>
    <tr>
        <td>funder</td>
        <td>MUST</td>
        <td>Array of <i>Funding Agency</i> or <i>Person</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"https://ror.org/00097mb19"}]</code></td>
        <td>研究費用の出資者</td>
        <td>common metadata:1.資金配分機関情報</td>
    </tr>
    <tr>
        <td>dmpFormat</td>
        <td>MUST</td>
        <td>Choose one from the list: common metadata; JST; AMED; METI</td>
        <td>DMPの様式</td>
        <td>検証時、ルールセット呼び出しに利用</td>
    </tr>
    <tr>
        <td>identifier</td>
        <td>MUST</td>
        <td>Array of <i>RepositoryObject</i> and <i>PropertyValue</i> entities represented by each @id property. e.g.
            <code>[{"@id":"https://rdm.nii.ac.jp/abcde/"},{"@id":"#e-Rad:123456"}]</code>. </td>
        <td>データ識別子 (リポジトリ情報とe-Rad課題番号を含む)</td>
        <td>common metadata:2.e-Radの課題番号, 12.リポジトリURL・DOIリンク<br>JST:研究データの所在場所<br>AMED:リポジトリ情報,臨床研究情報の登録内容<br>METI:リポジトリ
        </td>
    </tr>
    <tr>
        <td>dateCreated</td>
        <td>MUST</td>
        <td>MUST be a string in ISO 8601 date format and MAY be a timestamp down to the millisecond. Time zone is in UTC
        </td>
        <td>RO-Crate作成日 (ライブラリ利用の場合自動生成)</td>
        <td></td>
    </tr>
    <tr>
        <td>datePublished</td>
        <td>MUST</td>
        <td>MUST be a string in ISO 8601 date format and SHOULD be specified to at least the precision of a day</td>
        <td>メタデータ掲載日<br>指定しない場合はdateCreatedと同値とする</td>
        <td>common metadata<br>6: 掲載日・掲載更新日</td>
    </tr>
    <tr>
        <td>creator</td>
        <td>MUST</td>
        <td>Array of <i>Person</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"https://orcid.com/0000-0001-2345-6789"}]</code></td>
        <td>データ作成者の一覧</td>
        <td>common metadata:13.データ作成者<br>AMED:データ関連人材</td>
    </tr>
    <tr>
        <td>maintainer</td>
        <td>MUST if common to all dmp entities</td>
        <td>Array of <i> Hosting Instituion</i> or <i>Person</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"https://orcid.com/0000-0001-2345-6789"}]</code></td>
        <td>データ管理機関・管理者</td>
        <td>common metadata:14.データ管理機関, 14.データ管理者<br>JST:研究責任者<br>AMED:データ管理機関, データ管理者<br>METI:管理者</td>
    </tr>
    <tr>
        <td>contactPoint</td>
        <td>MUST if common to all dmp entities</td>
        <td>Array of <i>ContactPoint</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"#mailto:contact@example.com"}]</code></td>
        <td>データ管理機関・管理者への連絡先</td>
        <td>common metadata:14.データ管理者の連絡先<br>JST:研究データの管理者の連絡先<br>AMED:データ管理者の連絡先</td>
    </tr>
    <tr>
        <td>license</td>
        <td>MUST if common to all dmp entities</td>
        <td>Array of <i>CreativeWork</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"https://creativecommons.org/licenses/by/4.0"}]</code></td>
        <td>ライセンス情報</td>
        <td>common metadata:11.管理対象データの利活用・提供方針<br>JST:公開可能な研究データの提供方法・体制<br>METI:研究開発データの利活用・提供方針</td>
    </tr>
    <tr>
        <td>accessRights</td>
        <td>MUST if common to all dmp entities</td>
        <td>Choose one from the list: open access; restricted access; embargoed access; metadata only access</td>
        <td>データセットへのアクセス状況</td>
        <td>common metadata:11.アクセス権<br>JST:研究データの取扱い方法<br>AMED:アクセス権<br>METI:公開レベル</td>
    </tr>
    <tr>
        <td>isAccessibleForFree</td>
        <td>MUST if accessRights has <i>restricted access</i></td>
        <td>boolean<br>ガバナンス: <code>false</code>の場合、<i>restricted access</i>になっているか</td>
        <td>データ利用時の有償・無償</td>
        <td>common metadata:11.管理対象データの利活用・提供方針<br>JST:公開可能な研究データの提供方法・体制<br>METI:研究開発データの利活用・提供方針</td>
    </tr>
    <tr>
        <td>availabilityStarts</td>
        <td>MUST if accessRights has <i>embargoed access</i></td>
        <td>MUST be a string in ISO 8601 date format<br>ガバナンス: 検証時点よりも未来の日付になっているか, アクセス権は限定公開か</td>
        <td>公開猶予の場合の公開予定日</td>
        <td>common metadata:11.公開予定日<br>JST:公開までの猶予期間<br>AMED:公開予定日<br>METI:秘匿期間</td>
    </tr>
    <tr>
        <td>usageInfo</td>
        <td>SHOULD</td>
        <td>Array of <i>CreativeWork</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"#usageInfo:1"}]</code></td>
        <td>その他引用時条件もしくは非公開の理由</td>
        <td>common metadata:11.管理対象データの利活用・提供方針<br>JST:公開可能な研究データの提供方法・体制<br>METI:秘匿理由</td>
    </tr>
    <tr>
        <td>distribution</td>
        <td>MUST if accessRights has <i>open access</i></i></td>
        <td>Array of <i>DataDownload</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"https://github.com/github/gitignore"}]</code></td>
        <td>データセットの配布情報</td>
        <td>JST:公開の方法<br>METI:プロジェクト終了後のリポジトリ</td>
    </tr>
    <tr>
        <td>keyword</td>
        <td>MUST with common metadata</td>
        <td>string<br>Multiple textual entries in a keywords list are typically delimited by commas, or by repeating the
            property.</td>
        <td>分野情報, キーワード</td>
        <td>common metadata:8.データの分野<br>AMED:データの種別</td>
    </tr>
    <tr>
        <td>hasPart</td>
        <td>MUST</td>
        <td>Array of <i>data entities</i>, represented by each @id property. e.g.
            <code>[{"@id":"input/"},{"@id":"input/parameters.txt"}]</code></td>
        <td>対象ファイル・ディレクトリの一覧</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/data-entities.html>reserachobject.org</td>
    </tr>
    <tr>
        <th colspan="5">DataEntity</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>MUST be either a URI Path relative to the RO Crate root, or an absolute URI. With directory, the name SHOULD
            end with <code>/.</code><br>File Data Entries with an @id URI outside the RO-Crate Root SHOULD at the time
            of RO-Crate creation be directly downloadable by a simple retrieval (e.g. HTTP GET), permitting redirections
            and HTTP/HTTPS authentication.</td>
        <td>対象ファイル・ディレクトリのパス</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#core-metadata-for-data-entities>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST have <i>File</i> with a file.<br>MUST have <i>Dataset</i> with a directory.<br>In all cases, @type MAY
            be an array in order to also specify a more specific type, e.g.
            <code>"@type": ["File", "ComputationalWorkflow"]</code></td>
        <td>対象データのタイプ</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#referencing-files-and-folders-from-the-root-data-entity>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string</td>
        <td>ファイル名もしくはディレクトリ名</td>
        <td></td>
    </tr>
    <tr>
        <td>dmpDataNumber</td>
        <td>MUST</td>
        <td>Array of <i>Datalist on DMP</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"#dmp:1"}]</code></td>
        <td>DMPにおけるデータNo.</td>
        <td>common metadata:4.データNo.<br>AMED:研究開発データ<br>METI:研究開発データNo.</td>
    </tr>
    <tr>
        <td>contentSize</td>
        <td>MUST</td>
        <td>string</td>
        <td>ファイルサイズ</td>
        <td>ガバナンスに利用</td>
    </tr>
    <tr>
        <td>encodingFormat</td>
        <td>SHOULD</td>
        <td><i>MIME type</i> e.g. <code> "application/pdf"</code><br>Can be added PRONUM entity</td>
        <td>ファイルタイプ</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#adding-detailed-descriptions-of-encodings>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>url</td>
        <td>MAY</td>
        <td>url</td>
        <td>ファイル・ディレクトリ自体への直接URL</td>
        <td></td>
    </tr>
    <tr>
        <td>sdDatePublished</td>
        <td>MUST if file from URI outside the RO-Crate Root</td>
        <td>MUST be a string in ISO 8601 date format</td>
        <td>外部ファイルの取得日時</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#web-based-data-entities>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>keyword</td>
        <td>MUST with AMED</td>
        <td>string<br>Multiple textual entries in a keywords list are typically delimited by commas, or by repeating the
            property.</td>
        <td>分野情報, キーワード</td>
        <td>AMED:データの種別</td>
    </tr>
    <tr>
        <th colspan="5">Datalist on DMP</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>data No. of dmp documents, e.g. <code>"#dmp:1"</code></td>
        <td>DMPにおけるデータNo.</td>
        <td>common metadata:4.データNo.<br>AMED:研究開発データ<br>METI:研究開発データNo.</td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>CreativeWork</i></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string</td>
        <td>DMPにおけるデータ名称</td>
        <td>common metadata:5.データの名称<br>JST:研究開発データ名称<br>AMED:データの名称<br>METI:研究開発データ名称</td>
    </tr>
    <tr>
        <td>description</td>
        <td>MUST</td>
        <td>string</td>
        <td>DMPにおけるデータの説明</td>
        <td>common metadata:7.データの説明<br>JST:データ概要<br>AMED:データの説明<br>METI:研究開発データの説明</td>
    </tr>
    <tr>
        <td>identifier</td>
        <td>MAY</td>
        <td>Array of <i>PropertyValue</i> entities represented by each @id property. e.g.
            <code>[{"@id":"#jRCT:jRCT1234567890"}]</code>. </td>
        <td>データ識別子</td>
        <td>AMED:臨床研究情報の登録内容</td>
    </tr>
    <tr>
        <td>creator</td>
        <td>MUST if different from the root data entity</td>
        <td>Array of <i>Person</i> entities with common metadata.<br>Array of <i>Affiliation</i> entities with JST and
            METI.</td>
        <td>データ作成者</td>
        <td>common metadata:13.データ作成者<br>JST:データ取得者<br>METI:取得者</td>
    </tr>
    <tr>
        <td>maintainer</td>
        <td>MUST if different from the root data entity</td>
        <td>Array of <i> Hosting Instituion</i> or <i>Person</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"https://orcid.com/0000-0001-2345-6789"}]</code></td>
        <td>データ管理機関・管理者</td>
        <td>common metadata:14.データ管理機関, 14.データ管理者<br>JST:データ取得者<br>METI:管理者</td>
    </tr>
    <tr>
        <td>contactPoint</td>
        <td>MUST with common metadata and if different from the root data entity</td>
        <td>Array of <i>ContactPoint</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"#mailto:contact@example.com"}]</code></td>
        <td>データ管理機関・管理者への連絡先</td>
        <td>common metadata:14.データ管理者の連絡先<br>METI:連絡先</td>
    </tr>
    <tr>
        <td>isAccessibleForFree</td>
        <td>MUST if accessRights has <i>restricted access</i> and different from the root data entity</td>
        <td>boolean</td>
        <td>データ利用時の有償・無償</td>
        <td>common metadata:11.管理対象データの利活用・提供方針<br>JST:公開可能な研究データの提供方法・体制<br>METI:研究開発データの利活用・提供方針</td>
    </tr>
    <tr>
        <td>license</td>
        <td>MUST if different from the root data entity</td>
        <td>Array of <i>CreativeWork</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"https://creativecommons.org/licenses/by/4.0"}]</code></td>
        <td>ライセンス情報</td>
        <td>common metadata:11.管理対象データの利活用・提供方針<br>JST:公開可能な研究データの提供方法・体制<br>METI:研究開発データの利活用・提供方針</td>
    </tr>
    <tr>
        <td>accessRights</td>
        <td>MUST if different from the root data entity</td>
        <td>Choose one from the list: open access; restricted access; embargoed access; metadata only access</td>
        <td>データセットへのアクセス状況</td>
        <td>common metadata:11.アクセス権<br>JST:研究開発データの公開/非公開の方針<br>AMED:アクセス権<br>METI:公開レベル</td>
    </tr>
    <tr>
        <td>availabilityStarts</td>
        <td>MUST if accessRights has <i>embargoed access</i> and different from the root data entity</td>
        <td>MUST be a string in ISO 8601 date format<br>ガバナンス: 検証時点よりも未来の日付になっているか, アクセス権は限定公開か</td>
        <td>公開猶予の場合の公開予定日</td>
        <td>common metadata:11.公開予定日<br>AMED:公開予定日<br>METI:秘匿期間</td>
    </tr>
    <tr>
        <td>usageInfo</td>
        <td>MAY</td>
        <td>Array of <i>CreativeWork</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"#usageInfo:1"}]</code></td>
        <td>その他引用時条件もしくは非公開の理由</td>
        <td>common metadata:11.管理対象データの利活用・提供方針<br>JST:研究開発データ保存・管理の方針,公開可能な研究データの提供方法・体制<br>METI:研究開発データの利活用・提供方針,秘匿理由
        </td>
    </tr>
    <tr>
        <td>contentSize</td>
        <td>MUST with AMED</td>
        <td>Choose one from the list: 1GB; 10GB; 100GB; 1TB; 1PB</td>
        <td>想定される最大ファイルサイズ</td>
        <td>common metadata:12.概略データ量<br>AMED:概略データ量<br>METI:想定データ量</td>
    </tr>
    <tr>
        <td>measurementTechnique</td>
        <td>MUST with METI</td>
        <td>string</td>
        <td>データの取得方法</td>
        <td>METI:取得方法</td>
    </tr>
    <tr>
        <td>encodingFormat</td>
        <td>MAY</td>
        <td><i>MIME type</i> e.g. <code> "application/pdf"</code></td>
        <td>ファイルフォーマット</td>
        <td>METI:加工方針</td>
    </tr>
    <tr>
        <th colspan="5">Creator / Data Manager</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>Must be reachable URL, ORCID is recommended</td>
        <td></td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#people>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>Person</i></td>
        <td></td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#people>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string<br>In order of firstname, familyname<br>ガバナンス: @idのURLから得られる情報と一致しているか</td>
        <td>研究者氏名, データ管理者氏名</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#people>researchobject.org</a><br>common
            metadata:13.データ作成者<br>JST:研究代表者<br>AMED:研究開発代表者,データ管理者,データ関連人材</td>
    </tr>
    <tr>
        <td>identifier</td>
        <td>MUST with data manager(common metadata)</td>
        <td>Array of <i>PropertyValue</i> entities represented by each @id property. e.g.
            <code>[{"@id":"#e-Rad:123456"}]</code>. </td>
        <td>人物固有のID (e-Rad研究者番号を含む)</td>
        <td>common metadata:13.データ作成者のe-Rad研究者番号</td>
    </tr>
    <tr>
        <td>affiliation</td>
        <td>MUST</td>
        <td>Array of <i>Affiliation</i> entities represented by each @id property. e.g.
            <code>[{"@id":"https://ror.org/04ksd4g47"}]</code>. </td>
        <td>研究者の所属先機関</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#people>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>contactPoint</td>
        <td>SHOULD with data manager</td>
        <td>Array of <i>ContactPoint</i> entities, represented by each @id property. e.g.
            <code>[{"@id":"#mailto:contact@example.com"}]</code></td>
        <td>データ管理者の連絡先</td>
        <td>common metadata:14.データ管理者の連絡先<br>AMED:データ管理者の連絡先</td>
    </tr>
    <tr>
        <td>email</td>
        <td>MUST</td>
        <td>email</td>
        <td>研究者のメールアドレス</td>
        <td></td>
    </tr>
    <tr>
        <td>jobTitle</td>
        <td>MUST with research representative in JST, AMED</td>
        <td>string, e.g. <code>"representative"</code></td>
        <td>研究者の肩書き</td>
        <td>JST:研究代表者<br>AMED:研究開発代表者</td>
    </tr>
    <tr>
        <th colspan="5">Affiliation / Hosting Institution / Funding Agency</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>Must be reachable URI, ROR is recommended</td>
        <td></td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#organizations-as-values>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>Organization</i></td>
        <td></td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#organizations-as-values>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string<br>ガバナンス: @idのURIから取得できる情報と一致しているか</td>
        <td>組織名</td>
        <td>common metadata:1.資金配分機関情報, データ管理機関<br>AMED:所属,データ管理機関</td>
    </tr>
    <tr>
        <td>alternateName</td>
        <td>MAY</td>
        <td>string</td>
        <td>組織名の別名</td>
        <td>複数言語利用時</td>
    </tr>
    <tr>
        <td>description</td>
        <td>MAY</td>
        <td>string</td>
        <td>組織の説明</td>
        <td></td>
    </tr>
    <tr>
        <td>address</td>
        <td>MUST with common metadata if organization is data maintainer</td>
        <td>string</td>
        <td>組織の住所</td>
        <td>common metadata:14.データ管理者の連絡先<br>AMED:データ管理者の所属先の住所</td>
    </tr>
    <tr>
        <th colspan="5">ContactPoint</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td><code>#mailto:{email}</code> or <code>#callto:{tel_number}</code></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>ContactType</i></td>
        <td></td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#contact-information>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>email</td>
        <td>Either <i>email</i> or <i>telephone</i> is REQUIRED</td>
        <td>email</td>
        <td>メールアドレス</td>
        <td>common metadata:14.データ管理者の連絡先<br>AMED:データ管理者の連絡先<br>METI:連絡先</td>
    <tr>
        <td>telephone</td>
        <td>Either <i>email</i> or <i>telephone</i> is REQUIRED</td>
        <td>Phone number<br>ガバナンス: 桁数が正しいか</td>
        <td>電話番号</td>
        <td>common metadata:14.データ管理者の連絡先<br>AMED:データ管理者の連絡先<br>METI:連絡先</td>
    <tr>
        <th colspan="5">License</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>Must be reachable URI</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>CreativeWork</i></td>
        <td></td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#licensing-access-control-and-copyright>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string<br>Should be in <a href="https://spdx.org/licenses/">SPDX License List</a></td>
        <td>ライセンス名</td>
        <td>common metadata:11.管理対象データの利活用・提供方針<br>JST:公開可能な研究データの提供方法・体制<br>METI:研究開発データの利活用・提供方針</td>
    </tr>
    <tr>
        <td>description</td>
        <td>MAY</td>
        <td>string</td>
        <td>ライセンス概要</td>
        <td></td>
    </tr>
    <tr>
        <th colspan="5">Data Usage Infomation</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST if add this entity</td>
        <td><code>#usageInfo:{number}</code></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST if add this entity</td>
        <td>MUST be <i>CreativeWork</i></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>description</td>
        <td>MUST if add this entity</td>
        <td>string</td>
        <td>データ利用方法詳細</td>
        <td>common metadata:11.管理対象データの利活用・提供方針<br>JST:非公開または公開を制限する理由,
            公開可能な研究データの提供方法・体制<br>AMED:非公開の理由<br>METI:研究開発データの利活用・提供方針, 秘匿理由</td>
    <tr>
        <th colspan="5">Repository</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>URI</td>
        <td></td>
        <td>common metadata:12.リポジトリURL・DOIリンク<br>AMED:リポジトリURL・DOIリンク<br>METI:リポジトリ</td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>RepositoryObject</i></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string</td>
        <td>リポジトリ名</td>
        <td>common metadata:12.リポジトリ情報<br>JST:研究開発データ保存・管理の方針<br>AMED:リポジトリ情報<br>METI:リポジトリ</td>
    </tr>
    <tr>
        <td>description</td>
        <td>MAY</td>
        <td>string</td>
        <td>リポジトリ概要</td>
        <td></td>
    </tr>
    <tr>
        <th colspan="5">Encoding Description</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST if add this entity</td>
        <td>SHOULD be PRONUM identifier</td>
        <td>ファイルタイプのPRONUM</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#adding-detailed-descriptions-of-encodings>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST if add this entity</td>
        <td>SHOULD be <i>Website</i></td>
        <td></td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#adding-detailed-descriptions-of-encodings>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST if add this entity</td>
        <td>string</td>
        <td>ファイルタイプの名称</td>
        <td><a
                href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#adding-detailed-descriptions-of-encodings>researchobject.org</a>
        </td>
    </tr>
    <tr>
        <th colspan="5">File Distribution</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST if add this entity</td>
        <td>Accessible URI</td>
        <td></td>
        <td>JST:公開の方法<br>METI:プロジェクト終了後のリポジトリ</td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST if add this entity</td>
        <td>MUST be <i>DataDownload</i></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>downloadUrl</td>
        <td>MUST if add this entity</td>
        <td>Accessible URL, which is the same as @id property</i></td>
        <td>データを取得可能なURL</td>
        <td>JST:公開の方法<br>METI:プロジェクト終了後のリポジトリ</td>
    <tr>
        <th colspan="5">e-Rad ID</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST if add this entity</td>
        <td><code>#e-Rad:{e-Rad ID}</code></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST if add this entity</td>
        <td>MUST be <i>PropertyValue</i></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>Select <code>e-Rad Project ID</code> or <code>e-Rad Researcher Number</code></td>
        <td>e-Rad番号の種別</td>
        <td>common metadata:2.e-Radの課題番号, 13.データ作成者のe-Rad研究番号, 14.データ管理者のe-Rad研究番号</td>
    </tr>
    <tr>
        <td>value</td>
        <td>MUST</td>
        <td>e-Rad ID<br>ガバナンス: 研究者番号の場合チェックデジットを確認</td>
        <td>e-RadのID</td>
        <td>common metadata:2.e-Radの課題番号, 13.データ作成者のe-Rad研究番号, 14.データ管理者のe-Rad研究番号</td>
    </tr>
    <tr>
        <th colspan="5">Other Identifier</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST if add this entity</td>
        <td>ID category and number, e.g.<code>#jRCT:{jRCT ID}</code></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST if add this entity</td>
        <td>MUST be <i>PropertyValue</i></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>name of data registry system</td>
        <td>データ登録システムの名称</td>
        <td>AMED:臨床研究情報の登録内容</td>
    </tr>
    <tr>
        <td>value</td>
        <td>MUST</td>
        <td>string</td>
        <td>登録しているID</td>
        <td>AMED:臨床研究情報の登録内容</td>
    </tr>
    <tr>
        <th colspan="5">Informed Consent</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST if add this entity</td>
        <td><code>#IC:{number}</code></td>
        <td></td>
        <td>AMED:個人同意（IC）の有無</td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST if add this entity</td>
        <td>MUST be <i>AgreeAction</i></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>object</td>
        <td>MUST if add this entity</td>
        <td>@id property of <i>Consent Form</i> entity<br>If the form is included in data entities, can be @id property
            of the entity</td>
        <td>同意書</td>
        <td>AMED:同意事項の範囲</td>
    </tr>
    <tr>
        <td>result</td>
        <td>MUST if add this entity</td>
        <td>@id property of <i>dmp Datalist</i> entity</td>
        <td>対応するdmpのデータNo.</td>
        <td></td>
    </tr>
    <tr>
        <th colspan="5">Consent Form</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST if add this entity</td>
        <td>If use AMED format <code>"https://www.amed.go.jp/content/000091653.pdf"</code> else
            <code>"#consentform:{number}"</code> or its URI</td>
        <td></td>
        <td>AMED:同意事項の範囲</td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST if add this entity</td>
        <td>MUST be <i>CreativeWork</i></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST if add this entity</td>
        <td>string</td>
        <td>同意書名</td>
        <td></td>
    </tr>
</table>
