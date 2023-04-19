# nii-dgを利用したガバナンス事例
以下では、nii-dg機能を利用する研究データガバナンスの一例として、 `sapporo-service` によるワークフロー実行結果の検証を行う流れを示す。 sapporo-serviceについてはこの[githubリポジトリ](https://github.com/sapporo-wes/sapporo-service)を参照のこと。

### 前提
- sapporoを用いたワークフロー実行の結果を、研究データとしてパッケージングしro-crateを生成する。この時、新たに定義した`sapporo` スキーマを利用している。
- sapporoは remote REST API server として扱う。ただし本事例においては、sapporoはnii-dgコンテナから `http://sapporo-service:1122` を介してアクセス可能なローカルサーバーを remote REST API server と見立てている。
- 検証として、以下の三点を確認している。
  1. ro-crate内の値に基づいて、ワークフローが再実行可能である
  2. 再実行のステータスが、ro-crateに記載されているステータスと同一である
  3. 再実行で得られた結果ファイルのサイズ・チェックサムが、ro-crateの値と同一である (ro-crateに記載がある場合のみ)


## sapporoサーバーの準備
[sapporo](https://github.com/sapporo-wes/sapporo-service)サーバーを docker container として起動する。
```bash
$ git clone https://github.com/sapporo-wes/sapporo-service.git
Cloning into 'sapporo-service'...
...
Resolving deltas: 100% (XXX/XXX), done.
$ cd sapporo-service
sapporo-service$ docker compose up -d
sapporo-service$ localhost:1122/service-info
{
  "auth_instructions_url":
  ...
}
```

## sapporoでのワークフロー実行と結果の取得
次に、sapporoでワークフローを実行し、`outputs/` 以下のファイルと `run_request.json` をダウンロードする。 本事例では、ワークフロー実行例として、curlリクエストを行う[シェルスクリプト](./initial_run.sh)を用いた。これは、[post_runs.sh](https://github.com/sapporo-wes/sapporo-service/blob/main/tests/curl_example/post_runs/cwltool/attach_all_files/post_runs.sh)の内容を一部リモートファイルのfetch方式に書き換えたものである。
```bash
$ source sapporo_example/initial_run.sh
{"run_id":"3a9bbc21-e078-4169-afd7-0d3109889328"}
$ curl localhost:1122/runs/3a9bbc21-e078-4169-afd7-0d3109889328
{"outputs":
...
}
$ curl -OL localhost:1122/runs/3a9bbc21-e078-4169-afd7-0d3109889328/data/run_request.json
```

また、[initial_run_dir](./initial_run)配下に実行結果の該当ファイルが格納されている。

```
initial_run_dir
├─ outputs
│   ├── ERR034597_1.small_fastqc.html
│   ├── ERR034597_1.small.fq.trimmed.1P.fq
│   ├── ERR034597_1.small.fq.trimmed.1U.fq
│   ├── ERR034597_1.small.fq.trimmed.2P.fq
│   ├── ERR034597_1.small.fq.trimmed.2U.fq
│   └── ERR034597_2.small_fastqc.html
└─ run_request.json
```

本事例では、上記ワークフロー実行+ファイルダウンロードは、[initial_run.py](./initial_run.py)の実行により行なっている。
```bash
$ python3 sapporo_example/initial_run.py
```

## パッケージング
nii-dgライブラリがインストールされたpython環境で、[packaging.py](./packaging.py)を実行することで、上記結果をro-crateとしてパッケージングしjsonを生成する。
検証に成功する[ro-crate](./complete/ro-crate-metadata.json), 失敗する[ro-crate](./failed/ro-crate-metadata.json)の2種が生成できるようになっているため、コマンドライン引数でどちらかを指定する。
```bash
$ python3 sapporo_example/packaging.py complete
$ python3 sapporo_example/packaging.py failed
```


## 検証実施
NII-DGのAPIサーバーの起動方法は[api-quick-start.md](../api-quick-start.md)を参照のこと。本事例では `localhost:5000` でAPIサーバーにアクセスできるものとする。
また、NII-DG サーバーから sapporo へ通信できるよう、本事例では nii-dg のネットワークに sapporo を追加している。
```bash
$ curl localhost:5000/healthcheck
{
  "message": "OK"
}
$ docker network connect nii-dg-network sapporo-service
```

エンドポイント`/validate`に生成したro-crate-metadata.jsonをリクエストボディとしてPOST通信を行うと、request_idが返ってくる。次にそのrequest_idをエンドポイントとしてGET通信を行い、検証が終わっていれば結果が返ってくる。

以下では検証が無事終了し、結果も問題がなかったため、statusが `COMPLETE`, resultsは空のリストになっている。
```bash
$ curl -X POST localhost:5000/validate -d @sapporo_example/complete/ro-crate-metadata.json -H "Content-Type: application/json"
{"request_id": "8d107027-2d80-4b8e-bd6c-4783286a0dd8"}
$ curl localhost:5000/8d107027-2d80-4b8e-bd6c-4783286a0dd8
{
  ...
  "requestId": "8d107027-2d80-4b8e-bd6c-4783286a0dd8",
  "results": [],
  "status": "COMPLETE"
}
```

以下では検証が無事終了したが、スキーマのルールに対して不適合な箇所が見つかっている。statusは `FAILED`で, resultsに修正のためのメッセージが `エンティティ・プロパティ・不適合理由` の組み合わせでリストになっている。

今回の例では、outputs/に含まれる2つのhtmlファイルが、ワークフローの実行日を内容として含んでいるため、初回実行時と検証実施時で差分が生まれてしまう。よってファイルサイズ・チェックサムがro-crateに記述された値と異なるため、検証の結果は失敗となっている。
```bash
$ curl -X POST localhost:5000/validate -d @sapporo_example/failed/ro-crate-metadata.json -H "Content-Type: application/json"
{"request_id": "8c28f892-a669-481e-9fa2-e119e5a146bb"}
$ curl localhost:5000/8d107027-2d80-4b8e-bd6c-4783286a0dd8
{
  ...
  "requestId": "8c28f892-a669-481e-9fa2-e119e5a146bb",
  "results": [
    {
      "entityId": "#sapporo-run",
      "props": "sapporo.SapporoRun:outputs, ERR034597_1.small_fastqc.html:contentSize",
      "reason": "The file size of ERR034597_1.small_fastqc.html, 592394B, does not match the `contentSize` value 592393B in <sapporo.File outputs/ERR034597_1.small_fastqc.html>."
    },
    {
      "entityId": "#sapporo-run",
      "props": "sapporo.SapporoRun:outputs, ERR034597_1.small_fastqc.html:sha256",
      "reason": "The hash of ERR034597_1.small_fastqc.html does not match the `sha256` value e8b481c75d81f97080d8d61b9a21558c91e94488cc89dd20d09de4f7171df32d in <sapporo.File outputs/ERR034597_1.small_fastqc.html>"
    },
    {
      "entityId": "#sapporo-run",
      "props": "sapporo.SapporoRun:outputs, ERR034597_2.small_fastqc.html:contentSize",
      "reason": "The file size of ERR034597_2.small_fastqc.html, 592566B, does not match the `contentSize` value 592565B in <sapporo.File outputs/ERR034597_2.small_fastqc.html>."
    },
    {
      "entityId": "#sapporo-run",
      "props": "sapporo.SapporoRun:outputs, ERR034597_2.small_fastqc.html:sha256",
      "reason": "The hash of ERR034597_2.small_fastqc.html does not match the `sha256` value 0f977665918cfebd9be552bb670c7c78cb70df83f1eb6af3303381062f9ff8d4 in <sapporo.File outputs/ERR034597_2.small_fastqc.html>"
    }
  ],
  "status": "FAILED"
}
```
