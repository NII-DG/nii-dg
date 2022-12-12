# Test

## 入力JSONの作成方法

### 研究データ
ライブラリ上で研究データのメタデータを取得しない場合は、JSONに以下を含める。
- dataset: オブジェクトの配列
    - name*: ファイル名, ディレクトリ名
    - path*: リポジトリ内でのパス
    - size*:ファイルサイズ
    - format: ファイルフォーマット(ファイルのみ)
    - dmp*: 該当するDMPのデータNo.
    - url: ファイル, ディレクトリへの直接URL

### common metadata様式
*は必須項目

**はいずれか必須
- dmpFormat*: `common_metadata`
- projectName*: プロジェクト名
- description: プロジェクトの説明
- fundingAgency*: 研究資金提供機関, オブジェクトの配列
    - name*: 機関名
    - ror**: RORレジストリのページ,urlとどちらか必須
    - url**: 機関のURL, rorといずれか必須
- e-RadProjectId: e-RadのプロジェクトID
- publishedDate: メタデータ公開日
- creator*: データ作成者, オブジェクトの配列
    - name*: 氏名
    - orcid**: ORCIDのページ,urlとどちらか必須
    - url**: 研究者のURL, orcidといずれか必須
    - email*: メールアドレス
- researchField*: 研究分野
- dmp情報*: オブジェクトの配列
    - dataNumber*: dmp上のデータNo.
    - title*: データの名称
    - description: データの説明
    - repository**: リポジトリ情報, オブジェクト
    - dataType: データ種別
    - creator*: データ作成者, オブジェクトの配列, 既に記載した人物と同一の場合はnameプロパティのみでよい
    - hostingInstitution*: データ管理機関, オブジェクト
        - name*: 機関名
        - ror**: RORレジストリのページ,urlとどちらか必須
        - url**: 機関のURL, rorといずれか必須
        - address: 機関の住所
    - dataManager*: データ管理者, オブジェクト, 既に記載した人物と同一の場合はnameプロパティのみでよい
    - maxFileSize: 概略データ量
    - license: ライセンス, オブジェクトで記載
        - url*: ライセンスのURL
        - name*: ライセンス名
    - accessRights*: アクセス権
    - freeOrConsideration: 有償/無償
    - availableFrom: 公開猶予の場合の公開予定日
    - citationInfo: その他データ利用のための情報
    - downloadUrl: 公開の場合、データを入手できる場所。オブジェクトで記載
        - url*: データを入手できるURL
        - name*: 名称


### AMED様式
TBU
### METI様式
TBU



## common_sample.json
- ライブラリの入力データサンプル
- 公的資金による研究データの管理・利活用に関する基本的な考え方に基づいて、GRDMから取得できるメタデータをベースにしている

## ro-crate-metadata.json
- 上記`common_sample.json`を入力としてライブラリを利用した場合に生成されるRO-Crate

## GRDM Metadata

[`./grdm_metadata.csv`](./grdm_metadata.csv)

- GakuNin RDM から出力されるメタデータ
- メタデータとして、データに付随するものとプロジェクトに付随するものがある
  - GRDM 上での `メタデータ編集` ボタン
- 研究が確定したら export button で確定
  - 編集ができなくなる
- 編集途中で required の field が埋まっていない場合も export できる
- https://www8.cao.go.jp/cstp/common_metadata_elements.pdf
  - 内閣府公式のメタデータ仕様
  - referred to https://schema.irdb.nii.ac.jp/ja/access_rights_vocabulary
  - https://github.com/NII-DG/maDMP-template
- [`common_sample.json`](./common_sample.json)
  - DG 機能の入力のための metadata
  - GRDM の csv などから何かしらの utility で生成する

### About header

- Funder
  - depend to project
  - 資金提供機関
  - enum from: JST, NEDO, AMED, BRAIN
  - required
- e-Rad project ID
  - depend to project
  - required
- Project name
  - depend to project
  - 自由入力
    - GRDM プロジェクト作成時の名前が自動入力される
  - required
- Data No.
  - depend to data (以降全て to data)
  - 別紙の DMP 内における data No.
    - そちらを見ながら GRDM 上の file に付与する
  - not required
- Title
  - required
  - 日本語と英語の両方入れて export 時にどちらかを選択する
- Date (Issued / Updated)
  - not required
- Description
  - required
  - 日本語と英語の両方入れて export 時にどちらかを選択する
- Research field
  - 選択
  - e.g., life science, IT, environment, nano-tech, energy, manufacturing, social, frontier, nature science, other, etc.
  - 基本的にプロジェクトのやつを引き継ぐ
  - required
- Data type
  - 基本は dataset
  - e.g., dataset, paper, poster, presentation, tech-paper, software, etc.
  - required
- File size
  - 集計される (directory 以下だとトラバースする)
  - not required
- Data utilization and provision policy(Free/Consideration)
  - ここだけプルダウン
  - required
- Data utilization and provision policy(License)
  - e.g., Apache2.0
  - required
- Data utilization and provision policy(citation information)
  - required
- Access rights
  - e.g., public, private, restricted, etc.
- Repository information
  - free text
  - not required
- Repository URL/ DOI link
  - free text
  - ファイルに対する RDM 上の URL が自動入力される (永続化 URL)
  - not required
- Creator Name
  - array to single field
    - 現状、複数人入力した場合、セミコロン区切りで一つの field になる
- Creator name identifier (e-Rad)
  - array to single field
    - 現状、複数人入力した場合、セミコロン区切りで一つの field になる
- Hosting institution
  - free text
  - required
- Data manager
  - free text
  - not required
- Data manager identifier (e-Rad)
  - free text
  - not required
- Contact of data manager
  - 電話番号のみ GRDM から反映される
  - required
- Remarks
  - 備考
  - free text
  - not required
