# NII-DG: Schema: sapporo

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## File
Represents a file that is part of the research project and derived from executing the workflow on the Sapporo-service, such as run_request.json.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root or an absolute URI that is downloadable. If the file originates from outside the repository, @id SHOULD be directly downloadable via a simple retrieval (e.g., HTTP GET), allowing redirections and HTTP/HTTPS authentication. The RO-Crate itself (ro-crate-metadata.json) is exempted. | `outputs/file_1.txt` |
| `name` | `str` | Required. | Represents the file name. | `file_1.txt` |
| `contentSize` | `str` | Optional. | MUST be an integer representing the file size suffixed by `B` as the unit, bytes. If necessary, use "KB", "MB", "GB", "TB", or "PB" as units. If this property is included, its value is compared to the size of the file generated from the re-execution. | `1560B` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. If this property is included, its value is compared to the hash of the file generated from the re-execution. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `contents` | `str` | Optional. | MUST be the contents of the file. This property is useful for small files that can be included in the metadata file. | `This is a text file.` |

## Dataset
Represents a directory that contains output files produced by workflow execution on Sapporo.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root (specified in the identifier property of RootDataEntity) or an absolute URI. MUST end with `/`. Specifies the path to the directory. | `outputs/` |
| `name` | `str` | Required. | Denotes the directory name. In most cases, the value is "outputs". | `outputs` |
| `hasPart` | `List[File]` | Required. | Contains a list of File entities that are output files of the workflow. The files listed in this property are compared against the results of the re-execution. | `[{"@id": "outputs/file_1.txt"}]` |

## SapporoRun
Represents the run information of Sapporo. The data contained in this entity is utilized to re-execute the workflow and verify the result.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be "#sapporo-run" | `#sapporo-run` |
| `workflow_params` | `str` | Optional. | Parameters intended for workflow execution. | `{"fastq_1": {"location": "ERR034597_1.small.fq.gz", "class": "File"}, "fastq_2": {"location": "ERR034597_2.small.fq.gz", "class": "File"}, "nthreads": 2}` |
| `workflow_type` | `str` | Optional. | The specification of the workflow language utilized. | `CWL` |
| `workflow_type_version` | `str` | Optional. | The version of the designated workflow language. | `v1.0` |
| `tags` | `str` | Optional. | A key-value pair map representing arbitrary metadata beyond the scope of workflow_params. | `{"workflow_name": "dockstore-tool-bamstats-cwl"}` |
| `workflow_engine_name` | `str` | Required. | Denotes the name of the workflow engine intended to run the workflow. | `cwltool` |
| `workflow_engine_parameters` | `str` | Optional. | Additional parameters that can be forwarded to the workflow engine. | `None` |
| `workflow_url` | `str` | Optional. | The URL of the CWL or WDL workflow document. | `https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/trimming_and_qc.cwl` |
| `workflow_name` | `str` | Optional. | The name used to execute the workflow registered within the sapporo-service. | `Example workflow` |
| `workflow_attachment` | `str` | Optional. | An array of files used to upload files required for workflow execution. | `[{"file_name": "ERR034597_2.small.fq.gz", "file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_2.small.fq.gz"}, {"file_name": "ERR034597_1.small.fq.gz", "file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_1.small.fq.gz"}]` |
| `sapporo_location` | `str` | Required. | Indicates the location of the sapporo-service. This MUST be a reachable URL. | `https://example.com/sapporo-service` |
| `state` | `str` | Required. | Denotes the state of the run. | `COMPLETED` |
| `outputs` | `Dataset` | Required. | Specifies a directory containing output files. Files within this directory are compared against the result of the re-execution. | `{"@id":"outputs/"}` |
