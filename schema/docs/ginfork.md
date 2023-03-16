# NII-DG: Schema: ginfork

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## GinMonitoring
Monitoring function for the GIN-fork platform.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be `#ginmonitoring`. | `#ginmonitoring` |
| `about` | `RootDataEntity` | Required. | MUST be `{"@id": "./"}`. Indicates this rule applies to the research project stated in RootDataEntity. | `{"@id": "./"}` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "1TB", "1PB"]` | Required. | MUST choose one from `1GB`, `10GB`, `100GB`, `1TB` and `1PB`. Indicates maximum of sum total file size included in the experiment package. | `100GB` |
| `workflowIdentifier` | `Literal["basic", "bio", "neuro"]` | Required. | MUST choose one from `basic`, `bio` and `neuro`. Indicates a kind of workflow used in the research workflow. | `bio` |
| `datasetStructure` | `Literal["with_code", "for_parameter"]` | Required. | MUST choose either `with_code` or `for_parameter`. Indicates a kind of dataset structure used in the research workflow. | `with_code` |
| `experimentPackageList` | `List[str]` | Required. | MUST be an array of directory path of experiment package. | `["experiment/exp1/"]` |
| `experimentParameterName` | `List[str]` | Required when datasetStructure is "for_parameter". | MUST be an array of directory path of experiment parameter. | `["parameter", "temp"]` |

## File
A file monitored in the GIN-fork platform.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root or an absolute URI. When the file is from outside this research project, @id SHOULD be directly downloadable by a simple retrieval (e.g., HTTP GET), permitting redirections and HTTP/HTTPS authentication. RO-Crate itself (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. | Indicates the file name. | `setting.txt` |
| `contentSize` | `str` | Required. | MUST be an integer of the file size with the suffix `B` as a unit, bytes. If necessary, you can also use "KB", "MB", "GB", "TB" and "PB" as a unit. It will be used in the validation of the size stated in GinMonitoring entity. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be MIME type. Do not use "x-" prefix in MIME type. Indicates file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is from outside this research project. | Indicates the date that the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |
| `experimentPackageFlag` | `bool` | Required. | Indicates whether the file is included in an experiment package.  MUST be a boolean. | `True` |
