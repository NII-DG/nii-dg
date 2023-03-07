# NII-DG: Schema: sapporo

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## File
A file included in the research project, e.g. text file, script file and images.
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
| `run_request` | `File` | Required. | run_request.json | `run_request.json` |
| `sapporo_config` | `File` | Required. | sapporo_config.json | `sapporo_config.json` |
| `state` | `str` | Required. | Run state. | `COMPLETED` |
| `outputs` | `Dataset` | Required. | Directory with output files. The files under this directory are compared with the result of the re-execution. | `outputs/` |
