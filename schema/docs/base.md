# NII-DG: Schema: formated_base

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## Affiliation

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. Must be URL of the organization and recommended ROR ID. | `https://ror.org/04ksd4g47` |
| `description` | `str` | Optional. Description of an organization. | `Japan's only general academic research institution seeking to create future value in the new discipline of informatics.` |
| `name` | `str` | Required. Name of an organization. | `National Institute of Informatics` |

## Creator

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. Must be URL of a creator and recommended ORCID ID. | `https://orcid.org/0000-0001-2345-6789` |
| `affiliation` | `Affiliation` | Required. Affiliation a creator belongs to. Must be @id term from DMP entity. | `{ "@id": "https://ror.org/04ksd4g47" }` |
| `alias` | `str` | Optional. Another writings of the name of a creator. | `イチロー` |
| `email` | `str` | Required. Email address of a creator. | `ichiro@example.com` |
| `name` | `str` | Required. Name of a creator. Must be in order of first name, family name. | `Ichiro Suzuki` |

## DMP

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. Must be data No. with prefix "#dmp:". Indicates data No. in DMP list. | `#dmp:1` |
| `accessRights` | `Literal["open access", "restricted access", "embargoed access", "metadata only access"]` | Required. When all data set have common access right, it can be ommited instead of added to RootDataEntity. Must choose one from the list, open access; restricted access; embargoed access; metadata only access. Indicate the availability of data set. | `open access` |
| `availabilityStarts` | `datetime` | Required when accessRights has embargoed access. MUST be a string in ISO 8601 date format. Be velified that the value is the future than the time of verification. | `2023-04-01` |
| `contentSize` | `Literal["1GB", "10GB", "100GB", "1TB", "1PB"]` | Optional. Must choose one from the list, 1GB; 10GB; 100GB; 1TB; 1PB. | `100GB` |
| `description` | `str` | Required. Indicates data description in DMP. | `Result data calculated by Newton's method` |
| `distribution` | `DataDownload` | Required when accessRights has open access. When all open-access data set is available from a single URL, it can be ommited instead of adding to RootDataEntity. Indicates where download url of data set. | `{ "@id": "https://zenodo.org/record/example" }` |
| `isAccessibleForFree` | `bool` | Required when accessRights has open access or restricted access. MUST be a boolean. True means data set is free to access, while False means consideration. When access rights has open access, must be True. | `True` |
| `name` | `str` | Required. Indicates data title in DMP. | `calculated data` |
| `usageInfo` | `str` | Optional. Explanation for citaion. | `Contact data manager before usage of this data set.` |

## DataDownload

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. Must be reachable URL. | `https://rdm.nii.ac.jp/example/` |
| `downloadUrl` | `str` | Required. URL for donwloding data set. Must be the same URL as @id term. | `https://zenodo.org/record/example` |

## Dataset

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be either a URI Path relative to the RO Crate root (stated in identifier term of RootDataEntity). Must end with "/". Indicats path to the directory. | `config/` |
| `name` | `str` | Required. Indicates directory name. | `config` |
| `url` | `str` | Optional. Must be direct URL to the directory. | `https://github.com/username/repository/directory` |

## File

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. MUST be either a URI Path relative to the RO Crate root (stated in identifier term of RootDataEntity) or an absolute URI. When the file from outside of the repository, @id SHOULD be directly downloadable by a simple retrieval (e.g. HTTP GET), permitting redirections and HTTP/HTTPS authentication. RO-Crate itself (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `contentSize` | `str` | Required. Must be integer of file size with a suffix "B" as a unit, bite. Be validated with the size listed in DMP. | `1560B` |
| `dmpDataNumber` | `DMP` | Required. Must be @id term from DMP entity. Indicates data number in DMP this file is included in. | `{ "@id": "#dmp:1" }` |
| `encodingFormat` | `str` | Optional. Must be MIME type. Indicates file format. | `text/plain` |
| `name` | `str` | Required. Indicates file name. | `setting.txt` |
| `sdDatePublished` | `datetime` | Required when the file from outside the RO-Crate Root. Indicates date the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |
| `url` | `str` | Optional. Must be direct URL to the file. | `https://github.com/username/repository/file` |

## Funder

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. Must be URL of the organization and recommended ROR ID. | `https://ror.org/04ksd4g47` |
| `description` | `str` | Optional. Description of funder. | `Japan's only general academic research institution seeking to create future value in the new discipline of informatics.` |
| `name` | `str` | Required. Name of the funder. | `National Institute of Informatics` |

## RepositoryObject

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. Must be URL of a repository. | `https://rdm.nii.ac.jp/example/` |
| `description` | `str` | Optional. Description of a repository. | `Repository managed by NII.` |
| `name` | `str` | Required. Name of a repository. | `Gakunin RDM` |

## RootDataEntity

| Property | Type | Description | Example |
| --- | --- | --- | --- |
| `@id` | `str` | Required. Must be "./" . | `./` |
| `creator` | `List[Creator]` | Required. Must be array of Person entities. Indicates all data creators involved in this research project. | `[{ "@id": "https://orcid.org/0000-0001-2345-6789" }]` |
| `dateCreated` | `str` | Required. MUST be a string in ISO 8601 date format and a timestamp down to the millisecond. Time zone is in UTC. Indicates timestamp the RO-Crate itself is created. | `2022-12-09T10:48:07.976+00:00` |
| `description` | `str` | Optional. Description of the research project | `This research project aims to reveal the affect of xxx.` |
| `distribution` | `DataDownload` | Optional. Can be added when access rights has "open access" and all open-access data set is available from a single URL. Indicates where download url of data set. | `{ "@id": "https://zenodo.org/record/example" }` |
| `funder` | `List[Funder]` | Required. Funding agencies of research project. Must be array of Funder entities. | `[ { "@id": "https://ror.org/04ksd4g47" }, { "@id": "https://ror.org/007f5s288" } ]` |
| `hasPart` | `List[Dataset | File]` | Required. Must be array of Dataset and File entities which indicate files and directories. | `[{ "@id": "config/" }, { "@id": "config/config.txt" }]` |
| `name` | `str` | Required. Title of the research project | `Sample Research` |
| `repository` | `RepositoryObject` | Optional. Can be added when all data set is managed in a single repository. Indicates where the data is managed. | `{ "@id": "https://github.com/username/repository" }` |

