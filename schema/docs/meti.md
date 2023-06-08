# NII-DG: Schema: meti

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## DMPMetadata
Metadata related to the research project which is the focal point of this data management plan.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be a name prefixed by `#`. | `#METI-DMP` |
| `about` | `RootDataEntity` | Required. | MUST be `{"@id": "./"}`. Indicates that this DMP pertains to the research project generating the data described in RootDataEntity. | `{"@id": "./"}` |
| `name` | `str` | Required. | MUST be `METI-DMP`. Specifies the DMP format utilized by your project. | `METI-DMP` |
| `funder` | `Organization` | Required. | The funding agency supporting the research project. MUST be an @id dictionary of the Organization entity. | `{"@id": "https://ror.org/01b9y6c26"}` |
| `creator` | `List[Person]` | Optional. | MUST be an array of @id dictionaries of Person entities. Represents all data creators involved in this research project. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `repository` | `RepositoryObject` | Applicable when all dataset management is consolidated in a single repository. | MUST be an @id dictionary of the RepositoryObject entity. Identifies the repository managing the data. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Applicable when accessRights provide `open access` and all open-access data sets are accessible from a single URL. | MUST be an @id dictionary of the DataDownload entity. Specifies the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `hasPart` | `List[DMP]` | Required. | MUST be an array of DMP entities encompassed within this DMP. If no data has been generated yet, it MUST be an empty list. | `[{ "@id": "#dmp:1" }, { "@id": "#dmp:2" }]` |

## DMP
Constitutes the content of a Data Management Plan (DMP) that is or will be submitted to the funding agency.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be a data number prefixed by `#dmp:`. Denotes the data number in the DMP list. | `#dmp:1` |
| `dataNumber` | `int` | Required. | Signifies the data number in the DMP. MUST match the number embedded in the value of the @id property. | `1` |
| `name` | `str` | Required. | Represents the data title in the DMP. | `Calculated Data` |
| `description` | `str` | Required. | Describes the nature of the data in the DMP. | `Result data calculated using Newton's method` |
| `hostingInstitution` | `HostingInstitution` | Required. | Identifies the institution hosting the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `wayOfManage` | `Literal["commissioned", "self-managed"]` | Required. | Specifies the management style for the data set. | `commissioned` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. | MUST select one from `open access`, `restricted access`, `embargoed access` and `metadata-only access`. Reveals the availability status of the data set. | `open access` |
| `reasonForConcealment` | `str` | Required when accessRights is set to `restricted access`, `embargoed access` or `metadata only access`. | Elucidates the reason behind any restrictions or embargo on the data set. | `To preserve market competitiveness for commercialization` |
| `availabilityStarts` | `str` | Required when accessRights is set to `embargoed access`. | MUST be a string in ISO 8601 date format. DG-Core verifies that the provided value is a future date at the time of verification. | `2030-04-01` |
| `creator` | `List[Organization]` | Required. | MUST be an array of Organization entities. Signifies the organization that created the data set. | `[{"@id": "https://ror.org/04ksd4g47"}]` |
| `measurementTechnique` | `str` | Optional. | Explains the technique used for data collection. | `Data obtained using simulation software.` |
| `isAccessibleForFree` | `bool` | Required when accessRights is `open access` or `restricted access`. | MUST be a boolean. `True` implies free access to the data set, while `False` denotes paid access. For `open access`, the value MUST be `True`. | `True` |
| `license` | `License` | Required when accessRights is `open access`. | MUST be an @id dictionary of a License entity. Identifies the license applied to the data. | `{"@id": "https://www.apache.org/licenses/LICENSE-2.0"}` |
| `usageInfo` | `str` | Optional. | Offers guidance for citing the data set. | `Please contact the data manager prior to using this data set.` |
| `repository` | `RepositoryObject` | Required. If the entire data set is managed in a single repository, this can be omitted and added to the DMPMetadata entity instead. | MUST be an @id dictionary of the RepositoryObject entity. Specifies the repository housing the data. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "over100GB"]` | Required when accessRights is `open access`. | MUST select one from `1GB`, `10GB`, `100GB`, and `over100GB`. Defines the maximum cumulative file size for this DMP condition. | `100GB` |
| `distribution` | `DataDownload` | Required when accessRights in the tied DMP entity is `open access`. When all open-access data sets are available from a single URL, this can be omitted and added to the DMPMetadata entity instead. | MUST be an @id dictionary of the DataDownload entity. Provides the download URL for the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `contactPoint` | `ContactPoint` | Required when accessRights is `open access`, `restricted access` or `embargoed access`. | MUST be an @id dictionary of the ContactPoint entity. Indicates the contact information. | `{ "@id": "#mailto:contact@example.com" }` |

## File
Represents a file associated with the research project, such as a text file, script file, or image.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the root directory of your repository (specified in DMP entity) or an absolute URI. If the file originates from outside the research project, @id SHOULD be a directly downloadable link enabling simple retrieval (e.g., HTTP GET), allowing redirections and HTTP/HTTPS authentication. The RO-Crate itself (ro-crate-metadata.json) is exempted. | `config/setting.txt` |
| `name` | `str` | Required. | Represents the name of the file. | `setting.txt` |
| `dmpDataNumber` | `DMP` | Required. | MUST be an @id dictionary of the DMP entity. Denotes the data number in the DMP that encompasses this file. | `{"@id": "#dmp:1"}` |
| `contentSize` | `str` | Required. | MUST be an integer representing the file size suffixed by `B` as the unit, bytes. If necessary, use "KB", "MB", "GB", "TB", or "PB" as units. This value will be utilized to validate the size listed in the DMP. | `1560B` |
| `encodingFormat` | `str` | Optional. | Optional. MUST be a MIME type. Specifies the file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL leading to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file originates from outside this research project. | Denotes the date when the file was procured. MUST be a string in ISO 8601 date format. | `2022-12-01` |
