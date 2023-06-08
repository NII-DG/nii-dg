# NII-DG: Schema: cao

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## DMPMetadata
Metadata pertaining to a research project, which is the subject of this data management plan.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST include a prefix `#` with the name. | `#CAO-DMP` |
| `about` | `RootDataEntity` | Required. | MUST be `{"@id": "./"}`. Indicates that this DMP pertains to a research project generating the data outlined in RootDataEntity. | `{"@id": "./"}` |
| `name` | `str` | Required. | MUST be `CAO-DMP`. Denotes the DMP format adopted by the project. | `CAO-DMP` |
| `funder` | `Organization` | Required. | The funding agency for the research project. MUST be the @id dictionary for the Organization entity. | `{"@id": "https://ror.org/01b9y6c26"}` |
| `repository` | `RepositoryObject` | Can be included when all data sets are managed within a single repository. | MUST be the @id dictionary of the RepositoryObject entity. Signifies the repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Can be added when `open access` is specified under accessRights in the related DMP entity and all open-access data sets are accessible from a single URL. | MUST be the @id dictionary of the DataDownload entity. Specifies the download URL for the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `keyword` | `str` | Required. | Denotes the research field of the project. | `Informatics` |
| `eradProjectId` | `str` | Required if your project possesses an e-Rad project ID. | Specifies the e-Rad project ID. | `123456` |
| `hasPart` | `List[DMP]` | Required. | MUST be an array of DMP entities included in this DMP. If no data has been generated yet, it MUST be an empty list. | `[{ "@id": "#dmp:1" }, { "@id": "#dmp:2" }]` |

## DMP
This includes contents from a data management plan that will or has been submitted to the funding agency.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the data number with the prefix `#dmp:`. This represents the data number in the DMP list. | `#dmp:1` |
| `dataNumber` | `int` | Required. | This represents the data number in DMP. It MUST correspond to the number in the @id property. | `1` |
| `name` | `str` | Required. | This signifies the title of the data in DMP. | `calculated data` |
| `description` | `str` | Required. | This provides a description of the data in DMP. | `Result data calculated by Newton's method` |
| `creator` | `List[Person]` | Required. | MUST be an array of @id dictionary of Person entities. It represents all the data creators involved in this DMP. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `keyword` | `str` | Required. | Represents the research field of the data set. Generally, it aligns with that of the research project stated in the DMPMetadata entity. | `Informatics` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. | MUST select one among `open access`, `restricted access`, `embargoed access`, and `metadata only access`. This denotes the data set's availability. | `open access` |
| `availabilityStarts` | `str` | Required if accessRights specifies `embargoed access`. | MUST be a string in the ISO 8601 date format. DG-Core will verify if the value is in the future at the time of verification. | `2030-04-01` |
| `isAccessibleForFree` | `bool` | Required if accessRights specifies `open access` or `restricted access`. | MUST be a boolean. `True` implies the data set is free to access, while `False` implies charges may apply. If accessRights specifies `open access`, it MUST be `True`. | `True` |
| `license` | `License` | Required if accessRights specifies `open access`. | MUST be an @id dictionary of the License entity. This represents the license applicable to the data. | `{"@id": "https://www.apache.org/licenses/LICENSE-2.0"}` |
| `usageInfo` | `str` | Optional. | Instructions for citing the data set. | `Contact data manager before usage of this data set.` |
| `repository` | `RepositoryObject` | Required. If all data sets are managed in a single repository, this can be omitted and instead added to the DMPMetadata entity. | MUST be an @id dictionary of the RepositoryObject entity. This signifies the repository managing the data. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Required if accessRights specifies `open access`. If all open-access data sets are accessible from a single URL, this can be omitted and instead added to the DMPMetadata entity. | MUST be an @id dictionary of the DataDownload entity. This signifies the download URL for the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "over100GB"]` | Optional. | MUST select one among `1GB`, `10GB`, `100GB`, and `over100GB`. This represents the maximum total file size included in this DMP. | `100GB` |
| `hostingInstitution` | `HostingInstitution` | Required. | Indicates the institution hosting the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `dataManager` | `Person` | Required. | Identifies the manager of the data set. | `{ "@id": "https://orcid.org/0000-0001-2345-6789" }` |

## Person
An individual who has contributed to the research project, such as a researcher.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be a URL corresponding to the individual. An ORCID ID is highly recommended. | `https://orcid.org/0000-0001-2345-6789` |
| `name` | `str` | Required. | The full name of the individual, presented in the format of first name followed by family name. | `Ichiro Suzuki` |
| `alias` | `str` | Optional. | An alternate name or nickname for the individual. | `S. Ichiro` |
| `affiliation` | `Organization` | Required. | The organization the individual is associated with. MUST be an @id dictionary of the Organization entity. | `{"@id": "https://ror.org/04ksd4g47"}` |
| `email` | `str` | Required. | The individual's email address. | `ichiro@example.com` |
| `telephone` | `str` | Optional. | The individual's telephone number. | `03-0000-0000` |
| `eradResearcherNumber` | `str` | Required when the individual is the data manager or possesses an e-Rad researcher number. | Represents the e-Rad researcher number if applicable. | `01234567` |

## File
A file associated with the research project, such as a text file, script file, or image.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the root directory of the repository (specified in the DMP entity) or an absolute URI. If the file originates outside of this research project, @id SHOULD be directly retrievable (e.g., via HTTP GET), allowing for redirections and HTTP/HTTPS authentication. RO-Crate metadata (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. | Denotes the name of the file. | `setting.txt` |
| `dmpDataNumber` | `DMP` | Required. | MUST be an @id dictionary of the DMP entity. This indicates the data number in the DMP that includes this file. | `{"@id": "#dmp:1"}` |
| `contentSize` | `str` | Required. | MUST be a numerical value followed by the suffix `B` denoting bytes. If needed, "KB", "MB", "GB", "TB", and "PB" can also be used. This will be utilized to validate the file size if a contentSize property is present in the DMP entity. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be a MIME type, indicating the file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file originates outside this research project. | Specifies the date the file was acquired. MUST be a string following the ISO 8601 date format. | `2022-12-01` |
