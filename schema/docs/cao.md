# NII-DG: Schema: cao

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## RootDataEntity

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be `./`. | `./` |
| `name` | `str` | Required. Title of the research project. | `Example Research Project` |
| `description` | `str` | Optional. Description of the research project. | `This research project aims to reveal the effect of xxx.` |
| `funder` | `List[Funder]` | Required. Funding agencies of the research project. MUST be an array of @id term of Organization entity. | `[{"@id": "https://ror.org/01b9y6c26"}]` |
| `dateCreated` | `str` | Required. MUST be a string in ISO 8601 date format and a timestamp down to milliseconds. The time zone is UTC. Indicates timestamp the RO-Crate itself was created. | `2022-12-09T10:48:07.976+00:00` |
| `creator` | `List[Person]` | Required. MUST be an array of @id term of Person entity. Indicates all data creators involved in this research project. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `repository` | `RepositoryObject` | Can be added when all data set is managed in a single repository. MUST be @id term of RepositoryObject entity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Can be added when access rights have `open access` and all open-access data set is available from a single URL. MUST be @id term of DataDownload entity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `keyword` | `str` | Required. Indicates research filed of the project. | `Informatics` |
| `identifier` | `Erad` | Required when your project has e-Rad project ID. MUST be @id term of PropertyValue entities. Indicates e-Rad project ID. | `{ "@id": "#e-Rad:123456" }` |
| `hasPart` | `List[Union[Dataset, File]]` | Required. MUST be an array of Dataset and File entities that indicate files and directories as subjects of data governance. | `[{"@id": "config/"}, {"@id": "config/config.txt"}]` |

## DMP

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be data No. with the prefix `#dmp:`. Indicates data No. in the DMP list. | `#dmp:1` |
| `name` | `str` | Required. Indicates data title in DMP. | `calculated data` |
| `description` | `str` | Required. Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `keyword` | `str` | Required. Indicates research filed of the data set. Basically it is the same as that of research project, stated in RootDataEntity. | `Informatics` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. MUST choose one from `open access`, `restricted access`, `embargoed access` and `metadata-only access`. Indicate the availability of the data set. | `open access` |
| `availabilityStarts` | `str` | Required when accessRights has `embargoed access`. MUST be a string in ISO 8601 date format. It will be verified in DG-Core that the value is the future than the time of verification. | `2023-04-01` |
| `isAccessibleForFree` | `bool` | Required when accessRights has `open access` or `restricted access`. MUST be a boolean. True means the data set is free to access, while False means consideration. When access rights have open access, MUST be True. | `True` |
| `license` | `License` | Required when accessRights has `open access`. MUST be a @id term of License entity. Indicates the license applied for the data. | `{"@id": "https://www.apache.org/licenses/LICENSE-2.0"}` |
| `usageInfo` | `str` | Optional. An explanation for citation. | `Contact data manager before usage of this data set.` |
| `repository` | `RepositoryObject` | Required. MUST be @id term of the RepositoryObject entity. When all data set is managed in a single repository, it can be omitted instead of adding to RootDataEntity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Required when accessRights has `open access`. MUST be @id term of the DataDownload entity. When all open-access data set is available from a single URL, they can be omitted instead of added to RootDataEntity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "over100GB"]` | Optional. MUST choose one from `1GB`, `10GB`, `100GB` and `over100GB`. Indicates maximum of sum total file size included in this DMP condition. | `100GB` |
| `hostingInstitution` | `HostingInstituion` | Required. Indicates hosting institution of the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `dataManager` | `Person` | Required. Indicates data manager of data set. | `{ "@id": "https://orcid.org/0000-0001-2345-6789" }` |

## Person

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be URL of the person. ORCID ID is recommended. | `https://orcid.org/0000-0001-2345-6789` |
| `name` | `str` | Required. Name of the person. MUST be in the order of first name, and family name. | `Ichiro Suzuki` |
| `alias` | `str` | Optional. Another writing of a name of the person. | `S. Ichiro` |
| `affiliation` | `Organization` | Required. Affiliation which the person belongs to. MUST be a @id term of the DMP entity. | `{"@id": "https://ror.org/04ksd4g47"}` |
| `email` | `str` | Required. Email address of the person. | `ichiro@example.com` |
| `telephone` | `str` | Optional. Phone number of the person. | `03-0000-0000` |
| `identifier` | `Erad` | Required when the person has e-Rad researcher number. MUST be @id term of Erad entities. Indicates e-Rad researcher number. | `{ "@id": "#e-Rad:001234567" }` |
