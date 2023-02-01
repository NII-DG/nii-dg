# NII-DG: Schema: amed

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## DMPMetadata
Metadata of research project that is the subject of this data management plan.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the name with prefix `#`. | `#AMED-DMP` |
| `about` | `RootDataEntity` | Required. | MUST be `{"@id": "./"}`. Indicates this DMP is about research project that the data stated in RootDataEntity are generated. | `{"@id": "./"}` |
| `name` | `str` | Required. | MUST be `AMED-DMP`. Indicates the DMP format used by your project. | `AMED-DMP` |
| `funder` | `Organization` | Required. | Funding agency of the research project (AMED in most cases). MUST be @id dictionary of Organization entity. When the funder property of RootDataEntity is also used, this Organization entity MUST be included in the funder list in RootDataEntity. | `{"@id": "https://ror.org/01b9y6c26"}` |
| `funding` | `str` | Required. | Indicates the name of funding program. | `Acceleration Transformative Research for Medical Innovation` |
| `chiefResearcher` | `Person` | Required. | MUST be @id dictionary of Person entity. Indicates chief researcher or representative of the research project. | `{"@id": "https://orcid.org/0000-0001-2345-6789"}` |
| `creator` | `List[Person]` | Required when hasPart property has DMP entities. | MUST be an array of @id dictionary of Person entity. Indicates all data creators involved in this research project. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `hostingInstitution` | `HostingInstitution` | Required when hasPart property has DMP entities. | Indicates hosting institution of the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `dataManager` | `Person` | Required when hasPart property has DMP entities. | Indicates data manager of data set. | `{ "@id": "https://orcid.org/0000-0001-2345-6789" }` |
| `repository` | `RepositoryObject` | Can be added when all data set is managed in a single repository. | MUST be @id dictionary of RepositoryObject entity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Can be added when accessRights in tied DMP entity has `Unrestricted Open Sharing` and all Unrestricted-Open-Sharing data set is available from a single URL. | MUST be @id dictionary of DataDownload entity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `hasPart` | `List[DMP]` | Required. | MUST be an array of DMP entity, which is included in this DMP. If no data is created yet, MUST be empty list. | `[{ "@id": "#dmp:1" }, { "@id": "#dmp:2" }]` |

## DMP
Data management plan for each data collection, e.g. creators of the data collection, access rights, and how to cite the data collection.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be data number with the prefix `#dmp:`. Indicates data number in the DMP list. | `#dmp:1` |
| `dataNumber` | `int` | Required. | Indicates data number of DMP. MUST be the same as the number included in the value of @id property. | `1` |
| `name` | `str` | Required. | Indicates data title in DMP. | `calculated data` |
| `description` | `str` | Required. | Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `keyword` | `str` | Required. | Indicates category of the data set. | `biological origin data` |
| `accessRights` | `Literal["Unshared", "Restricted Closed Sharing", "Restricted Open Sharing", "Unrestricted Open Sharing"]` | Required. | MUST choose one from `Unshared`, `Restricted Closed Sharing`, `Restricted Open Sharing` and `Unrestricted Open Sharing`. Indicates the availability of the data set. | `Unrestricted Open Sharing` |
| `availabilityStarts` | `str` | Required when accessRights has `Unshared` or `Restricted Closed Sharing`. If the dataset will not be open sharing because it contains personal information or for some other reason, this value is not required, but instead the reason of unshared or closed sharing MUST be described in the following property, reasonForConcealment. | MUST be a string in ISO 8601 date format. It will be verified in DG-Core that the value is the future than the time of verification. Indicates when the data will be open sharing status. | `2030-04-01` |
| `reasonForConcealment` | `str` | Required when accessRights has `Unshared` or `Restricted Closed Sharing` and availabilityStarts property is not included in this entity. | Reason of keep unshared or closed sharing status. | `Because the dataset contains personal information.` |
| `repository` | `RepositoryObject` | Required. When all data set is managed in a single repository, it can be omitted instead of adding to DMPMetadata entity. | Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Required when accessRights has `Unrestricted Open Sharing`. When all Unrestricted-Open-Sharing data set is available from a single URL, it can be omitted instead of adding to DMPMetadata entity. | MUST be @id dictionary of the DataDownload entity. Indicates where the download URL of the data set. | `{ "@id": "https://zenodo.org/record/example" }` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "over100GB"]` | Optional. | MUST choose one from `1GB`, `10GB`, `100GB` and `over100GB`. Indicates maximum of sum total file size included in this DMP condition. | `100GB` |
| `gotInformedConsent` | `Literal["yes", "no", "unknown"]` | Required. | MUST choose one from `yes`, `no` or `unknown`. Indicates whether you got informed consent from subjects. | `yes` |
| `informedConsentFormat` | `Literal["AMED", "other"]` | Required when gotInformedConsent has `yes`. | MUST be either `AMED` or `others`. Indicates format of informed consent you used in this research to collect data. Whichever format you used, it must include the agreement for possibility that the data, including personal information, will be provided to third parties for purposes other than academic research. | `AMED` |
| `identifier` | `List[ClinicalResearchRegistration]` | Optional. | MUST be array of @id dictionary of ClinicalResearchRegistration entity. When you use clinical research registry service (e.g. jRCT, UMIN-CTR), it can be added @id dictionary of ClinicalResearchRegistration entity of them. Indicates identifier of data set. | `[{"@id": "https://jrct.niph.go.jp/latest-detail/jRCT202211111111"}]` |

## File
A file included in the research project, e.g. text file, script file and images.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the top directory of your repository (stated in DMP entity) or an absolute URI. When the file is from outside this research project, @id SHOULD be directly downloadable by a simple retrieval (e.g., HTTP GET), permitting redirections and HTTP/HTTPS authentication. | `config/setting.txt` |
| `name` | `str` | Required. | Indicates the file name. | `setting.txt` |
| `dmpDataNumber` | `DMP` | Required. | MUST be @id dictionary of the DMP entity. Indicates data number in DMP that includes this file. | `{"@id": "#dmp:1"}` |
| `contentSize` | `str` | Required. | MUST be an integer of the file size with the suffix `B` as a unit, bytes. If necessary, you can also use "KB", "MB", "GB", "TB" and "PB" as a unit. It will be used in the validation of the size listed in DMP. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be MIME type. Do not use "x-" prefix in MIME type. Indicates file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is from outside this research project. | Indicates the date that the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |

## ClinicalResearchRegistration
Identifier information that is registered to clinical research Registration service.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be URL where your registered information is available. | `https://jrct.niph.go.jp/latest-detail/jRCT202211111111` |
| `name` | `str` | Required. | Name of the registry service. | `Japan Registry of Clinical Trials` |
| `value` | `str` | Required. | Indicates ID you got from the registry service. | `1234567` |
