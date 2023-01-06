# NII-DG: Schema: cao

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## DMPMetadata
Metadata of research project that is the subject of this data management plan.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the name with prefix `#`. | `#CAO-DMP` |
| `about` | `RootDataEntity` | Required. | MUST be `{"@id": "./"}`. Indicates this DMP is about research project that the data stated in RootDataEntity are generated. | `{"@id": "./"}` |
| `name` | `str` | Required. | MUST be `CAO-DMP`. Indicates the DMP format used by your project. | `CAO-DMP` |
| `creator` | `List[Person]` | Required. | MUST be an array of @id term of Person entity. Indicates all data creators involved in this research project. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `repository` | `RepositoryObject` | Can be added when all data set is managed in a single repository. | MUST be @id term of RepositoryObject entity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Can be added when accessRights in tied DMP entity has `open access` and all open-access data set is available from a single URL. | MUST be @id term of DataDownload entity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `keyword` | `str` | Required. | Indicates research filed of the project. | `Informatics` |
| `eradProjectId` | `str` | Required when your project has e-Rad project ID. | Indicates e-Rad project ID. | `123456` |
| `hasPart` | `List[DMP]` | Required. | MUST be an array of DMP entity, which is included in this DMP. | `[{ "@id": "#dmp:1" }, { "@id": "#dmp:2" }]` |

## DMP
Contents from data management plan that is (will be) submitted to the funding agency.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be data No. with the prefix `#dmp:`. Indicates data number in the DMP list. | `#dmp:1` |
| `name` | `str` | Required. | Indicates data title in DMP. | `calculated data` |
| `description` | `str` | Required. | Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `keyword` | `str` | Required. | Indicates research filed of the data set. Basically it is the same as that of research project, stated in DMPMetadata entityDMPMetadata entity. | `Informatics` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. | MUST choose one from `open access`, `restricted access`, `embargoed access` and `metadata-only access`. Indicates the availability of the data set. | `open access` |
| `availabilityStarts` | `str` | Required when accessRights has `embargoed access`. | MUST be a string in ISO 8601 date format. It will be verified in DG-Core that the value is the future than the time of verification. | `2023-04-01` |
| `isAccessibleForFree` | `bool` | Required when accessRights has `open access` or `restricted access`. | MUST be a boolean. `True` means the data set is free to access, while `False` means consideration. When accessRights has `open access`, MUST be `True`. | `True` |
| `license` | `License` | Required when accessRights has `open access`. | MUST be a @id term of License entity. Indicates the license applied for the data. | `{"@id": "https://www.apache.org/licenses/LICENSE-2.0"}` |
| `usageInfo` | `str` | Optional. | An explanation for citation. | `Contact data manager before usage of this data set.` |
| `repository` | `RepositoryObject` | Required. When all data set is managed in a single repository, it can be omitted instead of adding to DMPMetadata entity. | MUST be @id term of the RepositoryObject entity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Required when accessRights has `open access`. When all open-access data set is available from a single URL, it can be omitted instead of adding to DMPMetadata entity. | MUST be @id term of the DataDownload entity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "over100GB"]` | Optional. | MUST choose one from `1GB`, `10GB`, `100GB` and `over100GB`. Indicates maximum of sum total file size included in this DMP condition. | `100GB` |
| `hostingInstitution` | `HostingInstitution` | Required. | Indicates hosting institution of the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `dataManager` | `Person` | Required. | Indicates data manager of data set. | `{ "@id": "https://orcid.org/0000-0001-2345-6789" }` |

## Person
A person who contributes to the research project, e.g. researcher.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be URL of the person. ORCID ID is recommended. | `https://orcid.org/0000-0001-2345-6789` |
| `name` | `str` | Required. | Name of the person. MUST be in the order of first name, and family name. | `Ichiro Suzuki` |
| `alias` | `str` | Optional. | Another writing of a name of the person. | `S. Ichiro` |
| `affiliation` | `Organization` | Required. | Affiliation which the person belongs to. MUST be a @id term of the Organization entity. | `{"@id": "https://ror.org/04ksd4g47"}` |
| `email` | `str` | Required. | Email address of the person. | `ichiro@example.com` |
| `telephone` | `str` | Optional. | Phone number of the person. | `03-0000-0000` |
| `eradResearcherNumber` | `str` | Required when the person is data manager or has e-Rad researcher number. | Indicates e-Rad researcher number. | `001234567` |

## File
A file included in the research project, e.g. text file, script file and images.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the top directory of your repository (stated in DMP entity) or an absolute URI. When the file is from outside this research project, @id SHOULD be directly downloadable by a simple retrieval (e.g., HTTP GET), permitting redirections and HTTP/HTTPS authentication. RO-Crate itself (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. | Indicates the file name. | `setting.txt` |
| `dmpDataNumber` | `DMP` | Required. | MUST be @id term of the DMP entity. Indicates data number in DMP that includes this file. | `{"@id": "#dmp:1"}` |
| `contentSize` | `str` | Required. | MUST be an integer of the file size with the suffix `B` as a unit, bytes. If necessary, you can also use "KB", "MB", "GB", "TB" and "PB" as a unit. It will be used in the validation of the size listed in DMP. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be MIME type. Indicates file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is from outside this research project. | Indicates the date that the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |
