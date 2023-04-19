# nii-dg を利用したガバナンス事例

以下では、nii-dg 機能を利用した研究データガバナンスの一例として、 Sapporo によるワークフロー実行結果の検証を行う流れを示す。
Sapporo については [GitHub - sapporo-wes/sapporo-service](https://github.com/sapporo-wes/sapporo-service) を参照のこと。

## 前提

- Sapporo を用いたワークフロー実行の結果を、研究データとしてパッケージングし RO-Crate を生成する
- Sapporo と NII-DG REST API server は、Docker container として起動し、同一ネットワークに接続されている
- 検証として、以下の三点を確認する
  1. RO-Crate 内の値に基づいて、ワークフローが再実行可能である
  2. 再実行のステータスが、RO-Crate に記載されているステータスと同一である
  3. 再実行で得られた結果ファイルのサイズ・チェックサムが、RO-Crate の値と同一である (RO-Crate に記載がある場合のみ)

## 0.1. Sapporo and NII-DG REST API Server の起動

```bash
# At this directory (sapporo_example)
$ docker compose up -d
[+] Running 2/2
 ✔ Container sapporo-service  Running                                                                0.0s
 ✔ Container nii-dg           Started                                                                0.9s
$ docker compose ps
NAME                IMAGE                                       COMMAND                  SERVICE             CREATED              STATUS              PORTS
nii-dg              nii-dg                                      "tini -- python /app…"   nii-dg              12 seconds ago       Up 11 seconds       0.0.0.0:5000->5000/tcp
sapporo-service     ghcr.io/sapporo-wes/sapporo-service:1.4.9   "tini -- uwsgi --yam…"   sapporo-service     About a minute ago   Up About a minute   0.0.0.0:1122->1122/tcp
```

疎通確認として、

```bash
# Host -> Sapporo
$ curl localhost:1122/service-info
{
  "auth_instructions_url"...
}

# Host -> NII-DG REST API Server
$ curl localhost:5000/healthcheck
{"message":"OK"}

# NII-DG REST API Server -> Sapporo
$ docker compose exec nii-dg bash
# In container
$ apt update
$ apt install -y curl
$ curl sapporo-service:1122/service-info
{
  "auth_instructions_url"...
}
```

## 0.2. NII-DG library の install

`0.1. Sapporo and NII-DG REST API Server の起動` にて、起動した NII-DG container は、validation のためのものである。
この項では、packaging 用の nii-dg library を install する。

```bash
# root directory に移動する
$ cd ../
$ ls setup.py
setup.py
$ python3 -m pip install .
...
$ python3 -m pip list | grep nii-dg
nii-dg                 1.0.0
```

## 1. Sapporo でのワークフロー実行 (`execute_workflow.py`)

実行する workflow として、[trimming_and_qc.cwl](https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/trimming_and_qc.cwl) を用いる。
この workflow は CommonWorkflowLanguage (CWL) によって書かれており、FASTQ ファイル (塩基配列ファイル) を入力とし、FASTQC による QC と、Trimmomatic によるトリミングを行う。

workflow を `curl` を用いて実行する場合、以下のようになる。(下のコマンドの実行は skip してよい)

```bash
$ curl -X POST \
     -F 'workflow_params={"fastq_1":{"location":"ERR034597_1.small.fq.gz","class":"File"},"fastq_2":{"location":"ERR034597_2.small.fq.gz","class":"File"},"nthreads":2}' \
     -F 'workflow_type=CWL' \
     -F 'workflow_type_version=v1.0' \
     -F 'workflow_url=https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/trimming_and_qc.cwl' \
     -F 'workflow_engine_name=cwltool' \
     -F 'workflow_attachment=[{"file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_2.small.fq.gz","file_name": "ERR034597_2.small.fq.gz"},{"file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_1.small.fq.gz","file_name": "ERR034597_1.small.fq.gz"}]' \
     http://localhost:1122/runs
{'run_id': 'd45a404e-8d8a-43ac-bbf8-b686ee426062'}
```

この command を python で実装したものとして、`execute_workflow.py` であり、これを用いて、ワークフローを実行する。

```bash
$ python3 execute_workflow.py -h
usage: execute_workflow.py [-h] [endpoint]

positional arguments:
  endpoint    The endpoint to send the request (default: http://localhost:1122)

optional arguments:
  -h, --help  show this help message and exit

$ python3 execute_workflow.py http://localhost:1122
{'run_id': 'd45a404e-8d8a-43ac-bbf8-b686ee426062'}
```

Sapporo の `RUN_ID` は、出力される `d45a404e-8d8a-43ac-bbf8-b686ee426062` などである。
実際に Sapporo における run の状態の確認は、この `RUN_ID` を用いて行う。
(run の状態などの元の source は、`${PWD}/run` 以下に配置されている)

```bash
$ curl localhost:1122/runs/d45a404e-8d8a-43ac-bbf8-b686ee426062 | jq .state
"COMPLETE"
```

この state が `COMPLETE` になったら、次のステップに進む。

## 2. Sapporo でのワークフロー実行結果の取得 (`download_results.py`)

想定として、Sapporo は REST API Server として、例えばどこかの cloud instance にデプロイされている。
そのため、実行結果 (e.g., 出力ファイル, etc.) を Sapporo からダウンロードする必要がある。

そのためのスクリプトとして、`download_results.py` が用意されている。

```bash
$ python3 download_results.py -h
usage: download_results.py [-h] [endpoint] run_id [output_dir]

positional arguments:
  endpoint    The endpoint to send the request (default: http://localhost:1122)
  run_id      The RUN_ID of the executed workflow
  output_dir  The output directory to save the results (default: ./results)

optional arguments:
  -h, --help  show this help message and exit

$ python3 download_results.py http://localhost:1122 d45a404e-8d8a-43ac-bbf8-b686ee426062 ./results

$ tree results/
results/
├── outputs
│   ├── ERR034597_1.small_fastqc.html
│   ├── ERR034597_1.small.fq.trimmed.1P.fq
│   ├── ERR034597_1.small.fq.trimmed.1U.fq
│   ├── ERR034597_1.small.fq.trimmed.2P.fq
│   ├── ERR034597_1.small.fq.trimmed.2U.fq
│   └── ERR034597_2.small_fastqc.html
└── run_request.json

1 directory, 7 files
```

結果が `results` 以下にダウンロードされる。

## 3. NII-DG による RO-Crate の生成 (`package_ro_crate.py`)

前項で download した結果を、nii-dg library を用いて RO-Crate として packaging する。

```bash
$ python3 package_ro_crate.py -h
usage: package_ro_crate.py [-h] [sapporo_endpoint] [wf_results_dir]

positional arguments:
  sapporo_endpoint  The endpoint of Sapporo, which is as seen from NII-DG server
                    (default: http://sapporo-service:1122)
  wf_results_dir    The directory where the results of the workflow are stored
                    (default: ./results)

optional arguments:
  -h, --help        show this help message and exit

$ python3 package_ro_crate.py

$ ls ro-crate-metadata.json
ro-crate-metadata.json
$ head ro-crate-metadata.json
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    {
      "@id": "./",
      "@type": "Dataset",
      "hasPart": [
        {
          "@id": "outputs/ERR034597_1.small.fq.trimmed.2U.fq"
        },
```

## 4. NII-DG API Server による RO-Crate の検証

NII-DG API Server の詳細については、[api-quick-start.md](../api-quick-start.md)を参照のこと。
`0.1. Sapporo and NII-DG REST API Server の起動` より、`localhost:5000` に NII-DG API Server が起動している。

```bash
$ curl localhost:5000/healthcheck
{"message": "OK"}
```

`/validate` に生成した `ro-crate-metadata.json` を POST する。

```
$ curl -X POST -H "Content-Type: application/json" -d @./ro-crate-metadata.json http://localhost:5000/validate
{"request_id":"bd6f18a4-1599-41d2-bcbd-75f2cda2209d"}
```

レスポンスとして、`request_id` が返ってくる。
この `request_id` を用いて、`/{request_id}` に GET し、検証結果を取得する。

```bash
$ curl localhost:5000/bd6f18a4-1599-41d2-bcbd-75f2cda2209d
{
  "request": {
    "entityIds": [],
    "roCrate": {
      "@context": "https://w3id.org/ro/crate/1.1/context",
      "@graph": [
        {
          ...
        }
      ]
    }
  },
  "requestId": "bd6f18a4-1599-41d2-bcbd-75f2cda2209d",
  "results": [],
  "status": "COMPLETE"
}
```

検証に問題がなかったため、`status` が `COMPLETE` 、`results` は空のリストになっている。

---

検証に問題がある例 (例えば、出力ファイルの名前が一致しないなど) として、`./ro-crate-metadata.json` を編集する。

```bash
$ cp ./ro-crate-metadata.json ./ro-crate-metadata_failed.json
$ sed -i 's/ERR034597_1.small_fastqc.html/ERR034597_1.small_fastqc_failed.html/' ./ro-crate-metadata_failed.json
$ diff -u ./ro-crate-metadata.json ./ro-crate-metadata_failed.json
```

編集した RO-Crate `ro-crate-metadata_failed.json` を用いて、検証を実行する。

```bash
$ curl -X POST -H "Content-Type: application/json" -d @./ro-crate-metadata_failed.json http://localhost:5000/validate
{"request_id":"32012249-d8f7-4f64-b20d-853ea5be67b5"}

$ curl localhost:5000/32012249-d8f7-4f64-b20d-853ea5be67b5
{
  "request": {
    "entityIds": [],
    "roCrate": {
      "@context": "https://w3id.org/ro/crate/1.1/context",
      "@graph": [
        {
          ...
        }
      ]
    }
  },
  "requestId": "32012249-d8f7-4f64-b20d-853ea5be67b5",
  "results": [
    {
      "entityId": "#sapporo-run",
      "props": "sapporo.SapporoRun:outputs_ERR034597_1.small_fastqc.html",
      "reason": "The file ERR034597_1.small_fastqc.html is included in the result of re-execution, so File entity with @id ERR034597_1.small_fastqc.html is required in this crate."
    }
  ],
  "status": "FAILED"
}
```

検証に問題があったため、`status` が `FAILED` 、`results` に問題があることが示されている。
