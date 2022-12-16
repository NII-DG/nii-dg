# NII-DG: Schema: meti

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## DMP

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be data No. with the prefix `#dmp:`. Indicates data No. in the DMP list. | `#dmp:1` |
| `name` | `str` | Required. Indicates data title in DMP. | `calculated data` |
| `description` | `str` | Required. Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `hostingInstitution` | `HostingInstituion` | Required. Indicates hosting institution of the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `wayOfManage` | `Literal["commissioned", "self-managed"]` | Required. Indicated how the data set is managed. | `commissioned` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. MUST choose one from the list, open access; restricted access; embargoed access; or metadata-only access. Indicate the availability of the data set. | `open access` |
| `reasonForConcealment` | `str` | Required when accessRights has restricted access, embargoed access and metadata only access. Indicates why access to the data set is ristricted and embargoed. | `To ensure market competitiveness for commercialization` |
| `availabilityStarts` | `str` | Required when accessRights has embargoed access. MUST be a string in ISO 8601 date format. It will be verified in DG-Core that the value is the future than the time of verification. | `2023-04-01` |
| `creator` | `List[Affiliation]` | Required. MUST be an array of Affiliation entities. Indicates the organization which created the data set. | `[{"@id": "https://ror.org/04ksd4g47"}]` |
| `measurementTechnique` | `str` | Optional. An explanation of the technique for getting data. | `Obtained using simulation software.` |
| `isAccessibleForFree` | `bool` | Required when accessRights has open access or restricted access. MUST be a boolean. True means the data set is free to access, while False means consideration. When accessRights have open access, MUST be True. | `True` |
| `license` | `License` | Required when accessRights has open access. MUST be a @id term of License entity. Indicates the license applied for the data. | `{"@id": "https://www.apache.org/licenses/LICENSE-2.0"}` |
| `usageInfo` | `str` | Optional. An explanation for citation. | `Contact data manager before usage of this data set.` |
| `repository` | `RepositoryObject` | Required. MUST be @id term of the RepositoryObject entity. When all data set is managed in a single repository, it can be omitted instead of adding to RootDataEntity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "1TB", "1PB"]` | Required when accessRights has open access, restricted access or embargoed access. MUST choose one from 1GB, 10GB, 100GB, 1TB and 1PB. Indicates maximum of sum total file size included in this DMP condition. | `100GB` |
| `distribution` | `DataDownload` | Required when accessRights has open access. MUST be @id term of the DataDownload entity. When all open-access data set is available from a single URL, they can be omitted instead of added to RootDataEntity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `contactPoint` | `ContactPoint` | Required when accessRights has open access or restricted access. MUST be @id term of ContactPoint entity. Indicates contact information. | `{ "@id": "#mailto:contact@example.com" }` |

