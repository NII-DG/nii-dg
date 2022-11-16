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
        <td>Description</td>
        <td>Why needed</td>
    </tr>
    <tr>
       <th colspan="4">RootDataEntity</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td>MUST end with / and SHOULD be the string ./</td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>
        <td>MUST be <i>Dataset</i></td>
        <td><a href=https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#direct-properties-of-the-root-data-entity>researchobject.org</a></td>
    </tr>
    <tr>
        <td>name</td>
        <td>MUST</td>
        <td>title of research project</td>
        <td>common metadata<br>3: プロジェクト名</td>
    </tr>
    <tr>
        <td>description</td>
        <td>MAY</td>
        <td>description of research project</td>
        <td>Gakunin RDM<br>プロジェクトの説明</td>
    </tr>
    <tr>
        <td>creator</td>
        <td>MUST</td>
        <td>Array of Person entities, represented by each @id property. e.g. <code>[{"@id":"https://orcid.com/0000-0001-2345-6789"}]</code></td>
        <td>common metadata<br>13: データ作成者</td>
    </tr>
    <tr>
        <td>contributer</td>
        <td>when data manager(データ管理者) is not included in creator, MUST</td>
        <td>Array of Person entities, represented by each @id property. e.g. <code>[{"@id":"https://orcid.com/0000-0001-2345-6789"}]</code></td>
        <td>common metadata<br>14: データ管理者</td>
    </tr>
    <tr>
       <th colspan="4">DataEntity</th>
    </tr>
    <tr>
        <td>@id</td>
        <td>MUST</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>@type</td>
        <td>MUST</td>                <td></td>
        <td></td>
    </tr>
    <tr>
       <th colspan="4">Datalist on DMP</th>
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
       <th colspan="4">Affiliation / Hosting Institution</th>
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