# NII Common Schema Profiles
## 対象としたdmp定義
- 「公的資金による研究データの管理・利活用に関する基本的な考え方」におけるメタデータの共通項目
    - 以下 `common metadata`とする
    - 参考: [PDF](https://www8.cao.go.jp/cstp/common_metadata_elements.pdf)

## profiles
<table>
    <tr>
        <td>Property</td>
        <td>Required?</td>
        <td>Format</td>
        <td>Description</td>
        <td>Why needed</td>
    </tr>
    <tr>
       <th colspan="5">RootDataEntity</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>MUST end with / and SHOULD be the string ./</td>
        <td></td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>Dataset</i></td>
        <td></td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a></td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string<br>SHOULD identify the dataset to humans well enough to disambiguate it from other RO-Crates</td>
        <td>title of research project</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a><br>common metadata:3.プロジェクト名</td>
    </tr>
    <tr>
        <td>description</td>
        <td>MAY</td>
        <td>string<br>SHOULD further elaborate on the name to provide a summary of the context in which the dataset is important.</td>
        <td>description of research project</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a><br>Gakunin RDM:プロジェクトの説明</td>
    </tr>
    <tr>
        <td>identifier</td>
        <td>MUST</td>
        <td>Array of <i>RepositoryObject</i> and <i>PropertyValue</i> entities represented by each @id property. e.g. <code>[{"@id":"https://rdm.nii.ac.jp/abcde/"},{"@id":"#e-Rad:123456"}]</code>. </td>
        <td>データ識別子 (リポジトリ情報とe-Rad課題番号を含む)</td>
        <td>common metadata:2.e-Radの課題番号, 12.リポジトリURL・DOIリンク</td>
    </tr>
     <tr>
        <td>dateCreated</td>
        <td>MUST</td>
        <td>Date</td>
        <td>RO-Crate作成日</td>
        <td></td>
    </tr>
     <tr>
        <td>datePublished</td>
        <td>MUST</td>
        <td>Date</td>
        <td>メタデータ掲載日<br>指定しない場合はRO-Crate作成日と同じとする</td>
        <td>common metadata<br>6: 掲載日・掲載更新日</td>
    </tr>
    <tr>
        <td>creator</td>
        <td>MUST</td>
        <td>Array of <i>Person</i> entities, represented by each @id property. e.g. <code>[{"@id":"https://orcid.com/0000-0001-2345-6789"}]</code></td>
        <td>データ作成者の一覧</td>
        <td>common metadata<br>13: データ作成者</td>
    </tr>
    <tr>
        <td>funder</td>
        <td>MUST</td>
        <td>Array of <i>Organization</i> or <i>Person</i> entities, represented by each @id property. e.g. <code>[{"@id":"https://orcid.com/0000-0001-2345-6789"}]</code></td>
        <td>研究費用の出資者</td>
        <td>common metadata<br>1: 資金配分機関情報</td>
    </tr>
     <tr>
        <td>dmpFormat</td>
        <td>MUST</td>
        <td>Choose one from the [list](#dmpformat-list)</td>
        <td>DMPの様式</td>
        <td>ガバナンスに利用</td>
    </tr>
    <tr>
        <td>maintainer</td>
        <td>Can be added to root data entity if commons to all dataset</td>
        <td>Array of <i>Organization</i> or <i>Person</i> entities, represented by each @id property. e.g. <code>[{"@id":"https://orcid.com/0000-0001-2345-6789"}]</code></td>
        <td>データ管理機関・管理者</td>
        <td>common metadata<br>14: データ管理機関, データ管理者</td>
    </tr>
    <tr>
        <td>contactPoint</td>
        <td>Set with <i>maintainer</i> property</td>
        <td>Array of <i>ContactPoint</i> entities, represented by each @id property. e.g. <code>[{"@id":"#mailto:contact@example.com"}]</code></td>
        <td>データ管理機関・管理者への連絡先</td>
        <td>common metadata<br>14: データ管理者の連絡先</td>
    </tr>
    <tr>
        <td>isAccessibleForFree</td>
        <td>Can be added to root data entity if commons to all dataset</td>
        <td>boolean</td>
        <td>データ利用時の有償・無償</td>
        <td>common metadata<br>11: 管理対象データの利活用・提供方針 </td>
    </tr>
    <tr>
        <td>license</td>
        <td>Can be added to root data entity if commons to all dataset</td>
        <td>Array of <i>CreativeWork</i> entities, represented by each @id property. e.g. <code>[{"@id":"https://creativecommons.org/licenses/by/4.0"}]</code></td>
        <td>ライセンス情報</td>
        <td>common metadata<br>11: 管理対象データの利活用・提供方針 </td>
    </tr>
    <tr>
        <td>usageInfo</td>
        <td>Can be added to root data entity if commons to all dataset</td>
        <td>Array of <i>CreativeWork</i> entities, represented by each @id property. e.g. <code>[{"@id":"#usageInfo:1"}]</code></td>
        <td>その他引用時条件等</td>
        <td>common metadata<br>11: 管理対象データの利活用・提供方針 </td>
    </tr>
    <tr>
        <td>accessRights</td>
        <td>Can be added to root data entity if commons to all dataset</td>
        <td>Choose one from the [list](#accessrights-list)</td>
        <td>データセットへのアクセス状況</td>
        <td>common metadata<br>11: アクセス権 </td>
    </tr>
    <tr>
        <td>availabilityStarts</td>
        <td>MUST if accessRights is <i>embargoed access</i></td>
        <td>Date</td>
        <td>公開猶予の場合の公開予定日</td>
        <td>common metadata<br>11: 公開予定日 </td>
    </tr>
    <tr>
        <td>distribution</td>
        <td>MUST if accessRights is <i>open access</i></td>
        <td>Array of <i>DataDownload</i> entities, represented by each @id property. e.g. <code>[{"@id":"https://github.com"}]</code></td>
        <td>データセットの配布情報</td>
        <td> </td>
    </tr>
  <tr>
        <td>keyword</td>
        <td>MUST</td>
        <td>string<br>Multiple textual entries in a keywords list are typically delimited by commas, or by repeating the property.</td>
        <td>分野情報, キーワード</td>
        <td>common metadata<br>8: データの分野</td>
    </tr>
    <tr>
        <td>hasPart</td>
        <td>MUST</td>
        <td>Array of <i>data entities</i>, represented by each @id property. e.g. <code>[{"@id":"input/"},{"@id":"input/parametors.txt"}]</code></td>
        <td>対象ファイル・ディレクトリの一覧</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/data-entities.html>reserachobject.org</td>
    </tr>
    <tr>
       <th colspan="5">DataEntity</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>MUST be either a URI Path relative to the RO Crate root, or an absolute URI. With directory, the id SHOULD end with /.<br>File Data Entries with an @id URI outside the RO-Crate Root SHOULD at the time of RO-Crate creation be directly downloadable by a simple retrieval (e.g. HTTP GET), permitting redirections and HTTP/HTTPS authentication.</td>
        <td>対象ファイル・ディレクトリのパス</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#core-metadata-for-data-entities>researchobject.org</a></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST have <i>File</i> with a file.<br>MUST have <i>Dataset</i> with a directory.<br>In all cases, @type MAY be an array in order to also specify a more specific type, e.g. <code>"@type": ["File", "ComputationalWorkflow"]</code></td>
        <td>対象データのタイプ</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#referencing-files-and-folders-from-the-root-data-entity>researchobject.org</a></td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>string</td>
        <td>ファイル名もしくはディレクトリ名</td>
        <td></td>
    </tr>
    <tr>
        <td>contentSize</td>
        <td>SHOULD</td>
        <td>string</td>
        <td>ファイルサイズ</td>
        <td>common metadata:12.概略データ量</td>
    </tr>
    <tr>
        <td>url</td>
        <td>MAY</td>
        <td>url</td>
        <td>ファイル・ディレクトリ自体への直接URL</td>
        <td>common metadata:12.リポジトリURL・DOIリンク</td>
    </tr>
    <tr>
        <td>sdDatePublished</td>
        <td>MUST if file from URI outside the RO-Crate Root</td>
        <td>date</td>
        <td>外部ファイルの取得日時</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/data-entities.html#web-based-data-entities>researchobject.org</a></td>
    </tr>
    <tr>
       <th colspan="5">Datalist on DMP</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">Creator</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">Affiliation / Hosting Institution / Funding Agency</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">ContactPoint</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">License</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">Repository</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">File Distribution</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">e-Rad ID</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">Data Usage Infomation</th>
    </tr>
        <tr>
        <td>@id</td>
        <td>must</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>must</td>                <td></td>
        <td></td>
    </tr>
</table>

## dmpFormat List
- common_metadata
- JST
- AMED
- NEDO
- BRAIN

## accessRights List
- open access
- restricted access
- embargoed access
- metadata only access
- 参考: [JPCOARスキーマガイドライン](https://schema.irdb.nii.ac.jp/ja/access_rights_vocabulary)