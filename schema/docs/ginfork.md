# NII-DG: Schema: ginfork

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## GinMonitoring
Monitoring functionality for the GIN-fork platform.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be `#ginmonitoring`. | `#ginmonitoring` |
| `about` | `RootDataEntity` | Required. | MUST be `{"@id": "./"}`. This rule applies to the research project declared in RootDataEntity. | `{"@id": "./"}` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "1TB", "1PB"]` | Required. | MUST select one from `1GB`, `10GB`, `100GB`, `1TB` or `1PB`. Specifies the maximum total file size included in the experiment package.' | `100GB` |
| `workflowIdentifier` | `Literal["basic", "bio", "neuro"]` | Required. | MUST select one from `basic`, `bio`, or `neuro`. Determines the type of workflow employed in the research workflow. | `bio` |
| `datasetStructure` | `Literal["with_code", "for_parameters"]` | Required. | MUST select either `with_code` or `for_parameters`. Defines the type of dataset structure used in the research workflow. | `with_code` |
| `experimentPackageList` | `List[str]` | Required. | MUST be an array representing the directory paths of experimental packages. | `["experiments/exp1/", "experiments/exp2/"]` |
| `parameterExperimentList` | `List[str]` | Required when datasetStructure is "for_parameters". | MUST be an array of directory paths pointing to the parameter folders within the experimental package. The path MUST be a subdirectory of one of the directories in the experimentPackageList. | `["experiments/exp1/ex_param1/", "experiments/exp1/ex_param2/", "experiments/exp2/paramX/"]` |

## File
A file under monitoring in the GIN-fork platform.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root or an absolute URI. If the file originates outside of this research project, @id SHOULD be directly retrievable (e.g., HTTP GET), allowing for redirections and HTTP/HTTPS authentication. The RO-Crate metadata file (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. | Denotes the name of the file. | `setting.txt` |
| `contentSize` | `str` | Required. | MUST be a numerical value followed by the suffix `B` denoting bytes. If needed, "KB", "MB", "GB", "TB", and "PB" can also be used. This will be utilized to validate the file size if a contentSize property is present in the GinMonitoring entity. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be a MIME type, without the "x-" prefix, indicating the file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file originates outside this research project. | Specifies the date the file was acquired. MUST be a string following the ISO 8601 date format. | `2022-12-01` |
| `experimentPackageFlag` | `bool` | Required. | Specifies if the file is included in an experiment package. MUST be a boolean. | `True` |
