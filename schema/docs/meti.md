# NII-DG: Schema: meti

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## DMPMetadata
Metadata of research project that is the subject of this data management plan.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the name with prefix `#`. | `#METI-DMP` |
| `about` | `RootDataEntity` | Required. | MUST be `{"@id": "./"}`. Indicates this DMP is about research project that the data stated in RootDataEntity are generated. | `{"@id": "./"}` |
| `name` | `str` | Required. | MUST be `METI-DMP`. Indicates the DMP format used by your project. | `METI-DMP` |
| `creator` | `List[Person]` | Required. | MUST be an array of @id term of Person entity. Indicates all data creators involved in this research project. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `repository` | `RepositoryObject` | Can be added when all data set is managed in a single repository. | MUST be @id term of RepositoryObject entity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Can be added when accessRights has `open access` and all open-access data set is available from a single URL. | MUST be @id term of DataDownload entity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `hasPart` | `List[DMP]` | Required. | MUST be an array of DMP entity, which is included in this DMP. | `[{ "@id": "#dmp:1" }, { "@id": "#dmp:2" }]` |

## DMP
Contents from data management plan that is (will be) submitted to the funding agency.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be data No. with the prefix `#dmp:`. Indicates data number in the DMP list. | `#dmp:1` |
| `name` | `str` | Required. | Indicates data title in DMP. | `calculated data` |
| `description` | `str` | Required. | Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `hostingInstitution` | `HostingInstitution` | Required. | Indicates hosting institution of the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `wayOfManage` | `Literal["commissioned", "self-managed"]` | Required. | Indicated how the data set is managed. | `commissioned` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. | MUST choose one from `open access`, `restricted access`, `embargoed access` and `metadata-only access`. Indicates the availability of the data set. | `open access` |
| `reasonForConcealment` | `str` | Required when accessRights has `restricted access`, `embargoed access` or `metadata only access`. | Indicates why access to the data set is ristricted and embargoed. | `To ensure market competitiveness for commercialization` |
| `availabilityStarts` | `str` | Required when accessRights has `embargoed access`. | MUST be a string in ISO 8601 date format. It will be verified in DG-Core that the value is the future than the time of verification. | `2023-04-01` |
| `creator` | `List[Organization]` | Required. | MUST be an array of Organization entities. Indicates the organization which created the data set. | `[{"@id": "https://ror.org/04ksd4g47"}]` |
| `measurementTechnique` | `str` | Optional. | An explanation of the technique for collecting data. | `Obtained using simulation software.` |
| `isAccessibleForFree` | `bool` | Required when accessRights has `open access` or `restricted access`. | MUST be a boolean. `True` means the data set is free to access, while `False` means consideration. When accessRights has `open access`, MUST be `True`. | `True` |
| `license` | `License` | Required when accessRights has `open access`. | MUST be a @id term of License entity. Indicates the license applied for the data. | `{"@id": "https://www.apache.org/licenses/LICENSE-2.0"}` |
| `usageInfo` | `str` | Optional. | An explanation for citation. | `Contact data manager before usage of this data set.` |
| `repository` | `RepositoryObject` | Required. When all data set is managed in a single repository, it can be omitted instead of adding to DMPMetadata entity. | MUST be @id term of the RepositoryObject entity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "over100GB"]` | Optional. | MUST choose one from `1GB`, `10GB`, `100GB` and `over100GB`. Indicates maximum of sum total file size included in this DMP condition. | `100GB` |
| `distribution` | `DataDownload` | Required when accessRights in tied DMP entity has `open access`. When all open-access data set is available from a single URL, it can be omitted instead of adding to DMPMetadata entity. | MUST be @id term of the DataDownload entity.Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `contactPoint` | `ContactPoint` | Required when accessRights has `open access` or `restricted access`. | MUST be @id term of ContactPoint entity. Indicates contact information. | `{ "@id": "#mailto:contact@example.com" }` |

## File
A file included in the research project, e.g. text file, script file and images.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the top directory of your repository (stated in DMP entity) or an absolute URI. When the file is from outside this research project, @id SHOULD be directly downloadable by a simple retrieval (e.g., HTTP GET), permitting redirections and HTTP/HTTPS authentication. RO-Crate itself (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. | Indicates the file name. | `setting.txt` |
| `dmpDataNumber` | `DMP` | Required. | MUST be @id term of the DMP entity. Indicates data number in DMP that includes this file. | `{"@id": "#dmp:1"}` |
| `contentSize` | `str` | Required. | MUST be an integer of the file size with the suffix `B` as a unit, bytes. If necessary, you can also use "KB", "MB", "GB", "TB" and "PB" as a unit. It will be used in the validation of the size listed in DMP. | `1560B` |
| `encodingFormat` | `str` | Optional. | Optional. MUST be MIME type. Indicates file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is from outside this research project. | Indicates the date that the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |
