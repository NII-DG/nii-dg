# NII-DG: Schema: amed

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## DMPMetadata
Metadata pertaining to the research project that this data management plan concerns.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be a string prefixed with '#'. | `#AMED-DMP` |
| `about` | `RootDataEntity` | Required. | MUST be `{"@id": "./"}`. This represents the research project producing the data encapsulated in the RootDataEntity. | `{"@id": "./"}` |
| `name` | `str` | Required. | MUST be `AMED-DMP`. This signifies the DMP format employed by your project. | `AMED-DMP` |
| `funder` | `Organization` | Required. | The funding entity for the research project, typically AMED. MUST be the @id dictionary of an Organization entity. | `{"@id": "https://ror.org/01b9y6c26"}` |
| `funding` | `str` | Required. | Denotes the name of the funding program. | `Acceleration Transformative Research for Medical Innovation` |
| `chiefResearcher` | `Person` | Required. | MUST be the @id dictionary of a Person entity. Indicates the principal researcher or project representative. | `{"@id": "https://orcid.org/0000-0001-2345-6789"}` |
| `creator` | `List[Person]` | Required when the hasPart property contains DMP entities. | MUST be an array of @id dictionaries of Person entities. Identifies all data creators participating in this research project. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `hostingInstitution` | `HostingInstitution` | Required when the hasPart property contains DMP entities. | Specifies the institution hosting the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `dataManager` | `Person` | Required when the hasPart property contains DMP entities. | Denotes the data set's manager. | `{ "@id": "https://orcid.org/0000-0001-2345-6789" }` |
| `repository` | `RepositoryObject` | Can be added when the entire data set is managed in a single repository. | MUST be the @id dictionary of a RepositoryObject entity. Indicates the repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Can be added when the accessRights in the associated DMP entity is set to `Unrestricted Open Sharing` and all Unrestricted-Open-Sharing data set is accessible from a single URL. | MUST be the @id dictionary of a DataDownload entity. Specifies the data set's download URL. | `{"@id": "https://zenodo.org/record/example"}` |
| `hasPart` | `List[DMP]` | Required. | MUST be an array of DMP entities included in this DMP. If no DMP is included, it MUST be an empty array. | `[{ "@id": "#dmp:1" }, { "@id": "#dmp:2" }]` |

## DMP
A data management plan (DMP) detailing individual data collections, inclusive of information on data collection creators, access rights, and data citation guidelines.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be a data identifier prefixed by `#dmp:`. Denotes the data number within the DMP list. | `#dmp:1` |
| `dataNumber` | `int` | Required. | Represents the DMP data number. MUST coincide with the number included in the value of the @id property. | `1` |
| `name` | `str` | Required. | Specifies the title of the data in the DMP. | `Calculated Data` |
| `description` | `str` | Required. | Provides a detailed description of the data in the DMP. | `Data derived through Newton's method` |
| `keyword` | `str` | Required. | Indicates the specific category of the data set. | `Biological Origin Data` |
| `accessRights` | `Literal["Unshared", "Restricted Closed Sharing", "Restricted Open Sharing", "Unrestricted Open Sharing"]` | Required. | MUST select one from `Unshared`, `Restricted Closed Sharing`, `Restricted Open Sharing`, or `Unrestricted Open Sharing`. This signifies the data set's availability. | `Unrestricted Open Sharing` |
| `availabilityStarts` | `str` | Required when accessRights is either `Unshared` or `Restricted Closed Sharing`. If the dataset cannot be openly shared due to the presence of personal information or other similar reasons, this value isn't needed. However, the reason for the unshared or closed sharing status MUST be detailed in the following property, reasonForConcealment. | MUST be a string in ISO 8601 date format. DG-Core will confirm that the value is set to a future date at the time of verification. Specifies when the data will transition to an open sharing status. | `2030-04-01` |
| `reasonForConcealment` | `str` | Required when accessRights is either `Unshared` or `Restricted Closed Sharing` and the availabilityStarts property isn't included in this entity. | Explains the reason for maintaining an unshared or closed sharing status. | `The dataset includes personal information.` |
| `repository` | `RepositoryObject` | Required. Can be omitted when the entire dataset is managed in a single repository, instead of being added to the DMPMetadata entity. | Identifies the repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Required when accessRights is `Unrestricted Open Sharing`. Can be omitted when all unrestricted open-sharing data sets are available from a single URL, instead of being added to the DMPMetadata entity. | MUST be an @id dictionary of the DataDownload entity. Specifies the data set's download URL. | `{ "@id": "https://zenodo.org/record/example" }` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "over100GB"]` | Optional. | MUST select one from `1GB`, `10GB`, `100GB`, and `over100GB`. Denotes the maximum cumulative file size encompassed in this DMP. | `100GB` |
| `gotInformedConsent` | `Literal["yes", "no", "unknown"]` | Required. | MUST select one from `yes`, `no`, or `unknown`. Specifies whether informed consent was obtained from the subjects. | `yes` |
| `informedConsentFormat` | `Literal["AMED", "other"]` | Required when gotInformedConsent is `yes`. | MUST be either `AMED` or `other`. Denotes the format of the informed consent utilized in this research for data collection. Regardless of the format employed, it MUST include an agreement acknowledging the potential provision of data, including personal information, to third parties for purposes beyond academic research. | `AMED` |
| `identifier` | `List[ClinicalResearchRegistration]` | Optional. | MUST be an array of @id dictionary of the ClinicalResearchRegistration entity. When using a clinical research registry service (e.g., jRCT, UMIN-CTR), an @id dictionary of the ClinicalResearchRegistration entity from those services can be added. This represents the identifier of the data set. | `[{"@id": "https://jrct.niph.go.jp/latest-detail/jRCT202211111111"}]` |

## File
A file associated with the research project, such as a text file, script file, or images.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the root directory of your repository (specified in DMP entity) or an absolute URI. If the file originates from outside this research project, the @id SHOULD facilitate direct download via a simple retrieval (e.g., HTTP GET), including redirections and HTTP/HTTPS authentication. | `config/setting.txt` |
| `name` | `str` | Required. | Denotes the file name. | `setting.txt` |
| `dmpDataNumber` | `DMP` | Required. | MUST be an @id dictionary of the DMP entity. Denotes the data number in the DMP that includes this file. | `{"@id": "#dmp:1"}` |
| `contentSize` | `str` | Required. | MUST be an integer followed by the `B` suffix denoting bytes as the unit of file size. Other permissible units include "KB", "MB", "GB", "TB", and "PB". This property is utilized during validation of the size listed in the DMP. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be a MIME type. Avoid using the "x-" prefix in MIME types. Specifies the file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is from outside this research project. | Denotes the date the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |

## ClinicalResearchRegistration
Identifier information registered with a clinical research registration service.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the URL where your registered information can be accessed. | `https://jrct.niph.go.jp/latest-detail/jRCT202211111111` |
| `name` | `str` | Required. | Specifies the name of the registration service. | `Japan Registry of Clinical Trials` |
| `value` | `str` | Required. | Denotes the ID received from the registration service. | `1234567` |
