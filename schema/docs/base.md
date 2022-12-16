# NII-DG: Schema: base

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## RootDataEntity

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be "./". | `./` |
| `name` | `str` | Required. Title of the research project. | `Example Research Project` |
| `description` | `str` | Optional. Description of the research project. | `This research project aims to reveal the effect of xxx.` |
| `funder` | `List[Funder]` | Required. Funding agencies of the research project. MUST be an array of Funder entities. | `[{"@id": "https://ror.org/01b9y6c26"}]` |
| `dateCreated` | `str` | Required. MUST be a string in ISO 8601 date format and a timestamp down to milliseconds. The time zone is UTC. Indicates timestamp the RO-Crate itself was created. | `2022-12-09T10:48:07.976+00:00` |
| `creator` | `List[Creator]` | Required. MUST be an array of Creator entities. Indicates all data creators involved in this research project. | `[{"@id": "https://orcid.org/0000-0001-2345-6789"}]` |
| `repository` | `RepositoryObject` | Can be added when all data set is managed in a single repository. Indicates repository where the data is managed. | `{ "@id": "https://doi.org/xxxxxxxx" }` |
| `distribution` | `DataDownload` | Optional. It can be added when access rights have "open access" and all open-access data set is available from a single URL. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `hasPart` | `List[Union[Dataset, File]]` | Required. MUST be an array of Dataset and File entities that indicate files and directories as subjects of data governance. | `[{"@id": "config/"}, {"@id": "config/config.txt"}]` |

## File

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be either a URI Path relative to the RO Crate root (stated in the identifier term of RootDataEntity) or an absolute URI. When the file is from outside the repository, @id SHOULD be directly downloadable by a simple retrieval (e.g., HTTP GET), permitting redirections and HTTP/HTTPS authentication. RO-Crate itself (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. Indicates file name. | `setting.txt` |
| `dmpDataNumber` | `DMP` | Required. MUST be a @id term from the DMP entity. Indicates data number in DMP this file is included in. | `{"@id": "#dmp:1"}` |
| `contentSize` | `str` | Required. MUST be an integer of file size with the suffix "B" as a unit, bytes. Be validated with the size listed in DMP. | `1560B` |
| `encodingFormat` | `str` | Optional. MUST be MIME type. Indicates file format. | `text/plain` |
| `url` | `str` | Optional. MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is from outside the RO-Crate Root. Indicates the date the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |

## Dataset

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be either a URI Path relative to the RO-Crate root (stated in the identifier term of RootDataEntity). MUST end with "/". Indicates the path to the directory. | `config/` |
| `name` | `str` | Required. Indicates directory name. | `config` |
| `url` | `str` | Optional. MUST be a direct URL to the directory. | `https://github.com/username/repository/directory` |

## DMP

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be data No. with the prefix "#dmp:". Indicates data No. in the DMP list. | `#dmp:1` |
| `name` | `str` | Required. Indicates data title in DMP. | `calculated data` |
| `description` | `str` | Required. Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. MUST choose one from the list, open access; restricted access; embargoed access; or metadata-only access. Indicate the availability of the data set. | `open access` |
| `availabilityStarts` | `str` | Required when accessRights has embargoed access. MUST be a string in ISO 8601 date format. It will be verified in DG-Core that the value is the future than the time of verification. | `2023-04-01` |
| `isAccessibleForFree` | `bool` | Required when accessRights has open access or restricted access. MUST be a boolean. True means the data set is free to access, while False means consideration. When access rights have open access, MUST be True. | `True` |
| `usageInfo` | `str` | Optional. An explanation for citation. | `Contact data manager before usage of this data set.` |
| `distribution` | `DataDownload` | Required when accessRights has open access. When all open-access data set is available from a single URL, they can be omitted instead of added to RootDataEntity. Indicates where the download URL of the data set. | `{"@id": "https://zenodo.org/record/example"}` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "1TB", "1PB"]` | Optional. MUST choose one from 1GB, 10GB, 100GB, 1TB and 1PB. Indicates maximum of sum total file size included in this DMP condition. | `100GB` |

## Funder

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be the URL of the organization and recommended ROR ID. | `https://ror.org/04ksd4g47` |
| `name` | `str` | Required. Name of the funder. | `National Institute of Informatics` |
| `description` | `str` | Optional. Description of a funder. | `Japan's only general academic research institution seeking to create future value in the new discipline of informatics.` |

## Creator

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be URL of the creator and recommended ORCID ID. | `https://orcid.org/0000-0001-2345-6789` |
| `name` | `str` | Required. Name of the creator. MUST be in the order of first name, and family name. | `Ichiro Suzuki` |
| `alias` | `str` | Optional. Another writing of a name of the creator. | `S. Ichiro` |
| `affiliation` | `Affiliation` | Required. Affiliation which the creator belongs to. MUST be a @id term from the DMP entity. | `{"@id": "https://ror.org/04ksd4g47"}` |
| `email` | `str` | Required. Email address of the creator. | `ichiro@example.com` |
| `telephone` | `str` | Optional. Phone number of the creator. | `03-0000-0000` |

## Affiliation

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be the URL of the organization and recommended ROR ID. | `https://ror.org/04ksd4g47` |
| `name` | `str` | Required. Name of the organization. | `National Institute of Informatics` |
| `description` | `str` | Optional. Description of the organization. | `Japan's only general academic research institution seeking to create future value in the new discipline of informatics.` |

## RepositoryObject

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be the URL of the repository. DOI link is recommended. | `https://doi.org/xxxxxxxx` |
| `name` | `str` | Required. Name of a repository. | `Gakunin RDM` |
| `description` | `str` | Optional. Description of a repository. | `Repository managed by NII.` |

## DataDownload

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be a reachable URL. | `https://rdm.nii.ac.jp/example/` |
| `downloadUrl` | `str` | Required. URL for downloading data sets. MUST be the same URL as the @id term. | `https://zenodo.org/record/example` |

## HostingInstitution

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be the URL of the organization and recommended ROR ID. | `https://ror.org/04ksd4g47` |
| `name` | `str` | Required. Name of the organization. | `National Institute of Informatics` |
| `description` | `str` | Optional. Description of the organization. | `Japan's only general academic research institution seeking to create future value in the new discipline of informatics.` |
| `address` | `str` | Required. Physical address of the organization. | `2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430` |

