# NII-DG: Schema: cabinet_office

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## RootDataEntity

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be "./". | `./` |
| `name` | `str` | Required. Title of the research project. | `Example Research Project` |
| `description` | `str` | Optional. Description of the research project. | `This research project aims to reveal the effect of xxx.` |
| `funder` | `List[Funder]` | Required. Funding agencies of the research project. MUST be an array of Funder entities. | `[{"@id": "https://ror.org/01b9y6c26"}]` |
| `dateCreated` | `str` | Required. MUST be a string in ISO 8601 date format and a timestamp down to milliseconds. The time zone is UTC. Indicates timestamp the RO-Crate itself was created. | `2022-12-09T10:48:07.976+00:00` |
| `creator` | `List[Creator]` | Required. MUST be an array of Person entities. Indicates all data creators involved in this research project. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `repository` | `RepositoryObject` | It can be added when all data set is managed in a single repository. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | It can be added when access rights have "open access" and all open-access data set is available from a single URL. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `keyword` | `str` | Required. Indicates research filed of the project. | `Informatics` |
| `identifier` | `Erad` | Required when your project has e-Rad project ID. MUST be @id term of PropertyValue entities. Indicates e-Rad project ID. | `{ "@id": "#e-Rad:123456" }` |
| `hasPart` | `List[Union[Dataset, File]]` | Required. MUST be an array of Dataset and File entities that indicate files and directories. | `[{"@id": "config/"}, {"@id": "config/config.txt"}]` |

## DMP

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be data No. with the prefix "#dmp:". Indicates data No. in the DMP list. | `#dmp:1` |
| `name` | `str` | Required. Indicates data title in DMP. | `calculated data` |
| `description` | `str` | Required. Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `keyword` | `str` | Required. Indicates research filed of the data set. Basically it is the same as that of research project, stated in RootDataEntity. | `Informatics` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required when all data sets have a common access right, they can be omitted instead of added to RootDataEntity. MUST choose one from the list, open access; restricted access; embargoed access; or metadata-only access. Indicate the availability of the data set. | `open access` |
| `availabilityStarts` | `str` | Required when accessRights has embargoed access. MUST be a string in ISO 8601 date format. Be verified that the value is the future than the time of verification. | `2023-04-01` |
| `isAccessibleForFree` | `bool` | Required when accessRights has open access or restricted access. MUST be a boolean. True means the data set is free to access, while False means consideration. When access rights have open access, MUST be True. | `True` |
| `license` | `License` | Required when accessRights has open access. MUST be a @id term of License entity. Indicates the license applied for the data. | `{"@id": "https://www.apache.org/licenses/LICENSE-2.0"}` |
| `usageInfo` | `str` | Optional. An explanation for citation. | `Contact data manager before usage of this data set.` |
| `repository` | `RepositoryObject` | Required. When all data set is managed in a single repository, it can be omitted instead of adding to RootDataEntity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Required when accessRights has open access. When all open-access data set is available from a single URL, they can be omitted instead of added to RootDataEntity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "1TB", "1PB"]` | Optional. MUST choose one from 1GB, 10GB, 100GB, 1TB and 1PB. | `100GB` |
| `hostingInstitution` | `HostingInstituion` | Must. Indicates hosting institution of the data set. | `[{ "@id": "https://ror.org/04ksd4g47" }]` |
| `dataManager` | `Creator` | Must. Indicates data manager of data set. | `[{ "@id": "https://orcid.org/0000-0001-2345-6789" }]` |

## Creator

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be the URL of a creator and recommended ORCID ID. | `https://orcid.org/0000-0001-2345-6789` |
| `name` | `str` | Required. Name of a creator. MUST be in the order of first name, and family name. | `Ichiro Suzuki` |
| `alias` | `str` | Optional. Another writing of the name of a creator. | `S. Ichiro` |
| `affiliation` | `Affiliation` | Required. Affiliation, a creator, belongs to. MUST be a @id term from the DMP entity. | `{"@id": "https://ror.org/04ksd4g47"}` |
| `email` | `str` | Required. Email address of a creator. | `ichiro@example.com` |
| `telephone` | `str` | Optional. Phone number of the creator. | `03-0000-0000` |
| `identifier` | `Erad` | Required when the creator has e-Rad researcher number. MUST be @id term of PropertyValue entities. Indicates e-Rad researcher number. | `{ "@id": "#e-Rad:001234567" }` |
| `jobTitle` | `str` | Required for data manager. The job title of the person. | `Data manager` |

## Erad

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. It must be ID with prefix "#e-Rad:". | `#e-Rad:1234567` |
| `name` | `Literal["e-Rad project ID", "e-Rad researcher number"]` | Required. Indicates a category of ID, project ID or researcher number. | `e-Rad project ID` |
| `value` | `str` | Required. ID or e-Rad. | `1234567` |

