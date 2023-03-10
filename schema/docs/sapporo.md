# NII-DG: Schema: sapporo

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## File
A file included in the research project and obtained from the execution of the workflow on Sapporo-service, e.g. run_request.json.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to RO-Crate root or an absolute URI from which is downloadable. When the file is from outside the repository, @id SHOULD be directly downloadable by a simple retrieval (e.g., HTTP GET), permitting redirections and HTTP/HTTPS authentication. RO-Crate itself (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `contentSize` | `str` | Optional. | MUST be an integer of the file size with the suffix `B` as a unit, bytes. If necessary, you can also use "KB", "MB", "GB", "TB" and "PB" as a unit. | `1560B` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `contents` | `str` | Optional. | MUST be the contents of the file. This is useful for small files that can be included in the metadata file. | `This is a text file.` |

## SapporoRun
A run information of a Sapporo. The value in this entity is used to re-execute the workflow and check the result.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be "#sapporo-run" | `#sapporo-run` |
| `workflow_params` | `str` | Optional. | Parameters for workflow execution. | `{"fastq_1":{"location":"ERR034597_1.small.fq.gz","class":"File"},"fastq_2":{"location":"ERR034597_2.small.fq.gz","class":"File"},"nthreads":2}"` |
| `workflow_type` | `str` | Optional. | The type of workflow language. | `CWL` |
| `workflow_type_version` | `str` | Optional. | The version of the workflow language. | `v1.0` |
| `tags` | `str` | Optional. | A key-value map of arbitrary metadata outside the scope of workflow_params. | `{"workflow_name": "dockstore-tool-bamstats-cwl"}` |
| `workflow_engine_name` | `str` | Required. | Specify the name of the workflow engine to run a workflow. | `cwltool` |
| `workflow_engine_parameters` | `str` | Optional. | Additional parameters can be sent to the workflow engine. | `None` |
| `workflow_url` | `str` | Optional. | The workflow CWL or WDL document. | `https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/trimming_and_qc.cwl` |
| `workflow_name` | `str` | Optional. | Name used to execute the workflow registered in the sapporo-service. | `Example workflow` |
| `workflow_attachment` | `str` | Optional. | The array of file used to upload files required to execute the workflow. | `[{"file_name": "ERR034597_2.small.fq.gz", "file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_2.small.fq.gz"}, {"file_name": "ERR034597_1.small.fq.gz", "file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_1.small.fq.gz"}]` |
| `sapporo_location` | `str` | Required. | The location where sapporo-service is. This MUST be accessible URL. | `https://example.com/sapporo-service` |
| `state` | `str` | Required. | Run state. | `COMPLETED` |
| `outputs` | `Dataset` | Required. | Directory with output files. The files under this directory are compared with the result of the re-execution. | `{"@id":"outputs/"}` |
