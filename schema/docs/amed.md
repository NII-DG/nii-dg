# NII-DG: Schema: amed

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## RootDataEntity

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be "./". | `./` |
| `name` | `str` | Required. Title of the research project. | `Example Research Project` |
| `description` | `str` | Optional. Description of the research project. | `This research project aims to reveal the effect of xxx.` |
| `funder` | `List[Funder]` | Required. Funding agencies of the research project. MUST be an array of Funder entities. | `[{"@id": "https://ror.org/01b9y6c26"}]` |
| `dateCreated` | `str` | Required. MUST be a string in ISO 8601 date format and a timestamp down to the millisecond. Time zone is in UTC. Indicates timestamp the RO-Crate itself is created. | `2022-12-09T10:48:07.976+00:00` |
| `creator` | `List[Creator]` | Required. MUST be an array of Creator entities. Indicates all data creators involved in this research project. | `[{ "@id": "https://orcid.org/0000-0001-2345-6789" }]` |
| `hostingInstitution` | `HostingInstituion` | Required. Indicates hosting institution of the data set. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `dataManager` | `Creator` | Required. Indicates data manager of data set. | `{ "@id": "https://orcid.org/0000-0001-2345-6789" }` |
| `repository` | `RepositoryObject` | Can be added when all data set is managed in a single repository. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Can be added when access rights has "open access" and all open-access data set is available from a single URL. Indicates where download url of data set. | `{ "@id": "https://zenodo.org/record/example" }` |
| `hasPart` | `List[Union[Dataset, File]]` | Required. MUST be an array of Dataset and File entities that indicate files and directories as subjects of data governance. | `[{ "@id": "config/" }, { "@id": "config/config.txt" }]` |

## DMP

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be data No. with prefix "#dmp:". Indicates data No. in DMP list. | `#dmp:1` |
| `name` | `str` | Required. Indicates data title in DMP. | `calculated data` |
| `description` | `str` | Required. Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `keyword` | `str` | Required. Indicates category of the data set. | `biological origin data` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. MUST choose one from the list, open access; restricted access; embargoed access; or metadata-only access. Indicate the availability of the data set. | `open access` |
| `availabilityStarts` | `str` | Required when accessRights has embargoed access. MUST be a string in ISO 8601 date format. It will be verified in DG-Core that the value is the future than the time of verification. | `2023-04-01` |
| `isAccessibleForFree` | `bool` | Required when accessRights has open access or restricted access. MUST be a boolean. True means the data set is free to access, while False means consideration. When access rights have open access, MUST be True. | `True` |
| `usageInfo` | `str` | Optional. An explanation for citation. | `Contact data manager before usage of this data set.` |
| `repository` | `RepositoryObject` | Required. When all data set is managed in a single repository, it can be omitted instead of adding to RootDataEntity. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Required when accessRights has open access. When all open-access data set is available from a single URL, it can be omitted instead of adding to RootDataEntity. Indicates where download url of data set. | `{ "@id": "https://zenodo.org/record/example" }` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "1TB", "1PB"]` | Required. MUST choose one from 1GB, 10GB, 100GB, 1TB and 1PB. Indicates maximum of sum total file size included in this DMP condition. | `100GB` |
| `gotInformedConsent` | `Literal["yes", "no", "unknown"]` | Required. MUST choose one from the list, yes; no; unknown. Indicates whether you got informed consent from subjects. | `yes` |
| `informedConsentFormat` | `Literal["AMED", "other"]` | Required when you got informed consent. MUST be either "AMED" or "others". Indicates format of informed consent you used in this research to collect data. Whichever format you used, it must include the agreement for possibility that the data, including personal information, will be provided to third parties for purposes other than academic research. | `AMED` |
| `identifier` | `PropertyValue` | Optional. When you use registry service (e.g. jRCT, UMIN-CTR), it can be added @id term of PropertyValue entity of them. Indicates identifier of data set. | `{"@id": "https://jrct.niph.go.jp/latest-detail/jRCT202211111111"}` |

## Creator

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be URL of the creator and recommended ORCID ID. | `https://orcid.org/0000-0001-2345-6789` |
| `name` | `str` | Required. Name of the creator. MUST be in the order of first name, and family name. | `Ichiro Suzuki` |
| `alias` | `str` | Optional. Another writing of a name of the creator. | `S. Ichiro` |
| `affiliation` | `Affiliation` | Required. Affiliation which the creator belongs to. MUST be a @id term from the DMP entity. | `{"@id": "https://ror.org/04ksd4g47"}` |
| `email` | `str` | Required. Email address of a creator. | `ichiro@example.com` |
| `telephone` | `str` | Optional. Phone number of the creator. | `03-0000-0000` |
| `jobTitle` | `str` | Required for chief researcher and data manager. The job title of the person. | `Chief reseacher, Data manager` |

## PropertyValue

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. URL of registrated data. When there is no URL, combine registry name and ID with prefix "#". | `#jRCT:1234567` |
| `name` | `str` | Required. Name of the data registry service. | `Japan Registry of Clinical Trials` |
| `value` | `str` | Required. ID you got from the registry service. | `1234567` |

