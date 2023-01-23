# NII-DG: Schema: base

See [GitHub - ascade/nii-dg - schema/README.md](https://github.com/ascade/nii-dg/blob/main/schema/README.md) for more information.

## RootDataEntity
A Dataset that represents the RO-Crate. For more information, see https://www.researchobject.org/ro-crate/1.1/root-data-entity.html .
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be `./`. | `./` |
| `name` | `str` | Required. | Title of the research project. | `Example Research Project` |
| `description` | `str` | Optional. | Description of the research project. | `This research project aims to reveal the effect of xxx.` |
| `funder` | `List[Organization]` | Optional. | Funding agencies of the research project. MUST be an array of @id dictionary of Organization entity. | `[{"@id": "https://ror.org/01b9y6c26"}]` |
| `dateCreated` | `str` | Required. | Automatically added to the entity when you generate RO-Crate with as_jsonld() method. MUST be a string in ISO 8601 date format and a timestamp down to milliseconds. The time zone is UTC. Indicates timestamp the RO-Crate itself was created. | `2022-12-09T10:48:07.976+00:00` |
| `hasPart` | `List[Union[Dataset, File]]` | Required. | MUST be an array of Dataset and File entities that indicate files and directories as subjects of data governance. If there is no file to include, MUST be empty list. | `[{"@id": "config/"}, {"@id": "config/config.txt"}]` |

## File
A file included in the research project, e.g. text file, script file and images.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to RO-Crate root or an absolute URI from which is downloadable. When the file is from outside the repository, @id SHOULD be directly downloadable by a simple retrieval (e.g., HTTP GET), permitting redirections and HTTP/HTTPS authentication. RO-Crate itself (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. | Indicates the file name. | `setting.txt` |
| `contentSize` | `str` | Required. | MUST be an integer of the file size with the suffix `B` as a unit, bytes. If necessary, you can also use "KB", "MB", "GB", "TB" and "PB" as a unit. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be MIME type. Do not use "x-" prefix in MIME type. Indicates file format. | `text/plain` |
| `sha256` | `str` | Optional. | Optional. MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is from outside the RO-Crate Root. | Indicates the date that the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |

## Dataset
A folder of the files included in the research project.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root (stated in the identifier property of RootDataEntity) or an absolute URI. MUST end with `/`. Indicates the path to the directory. | `config/` |
| `name` | `str` | Required. | Indicates directory name. | `config` |
| `url` | `str` | Optional. | MUST be a direct URL to the directory. | `https://github.com/username/repository/directory` |

## Organization
An organization related to the research project, e.g. university, research institution and funding agency.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the URL of the organization. ROR ID is recommended. | `https://ror.org/04ksd4g47` |
| `name` | `str` | Required. | Name of the organization. | `National Institute of Informatics` |
| `alias` | `str` | Optional. | Another writing of a name of the organization. | `NII` |
| `description` | `str` | Optional. | Description of the organization. | `Japan's only general academic research institution seeking to create future value in the new discipline of informatics.` |

## Person
A person who contributes to the research project, e.g. researcher.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be URL of the person. ORCID ID is recommended. | `https://orcid.org/0000-0001-2345-6789` |
| `name` | `str` | Required. | Name of the person. MUST be in the order of first name, and family name. | `Ichiro Suzuki` |
| `alias` | `str` | Optional. | Another writing of a name of the person. | `S. Ichiro` |
| `affiliation` | `Organization` | Required. | Affiliation which the person belongs to. MUST be a @id dictionary of the Organization entity. | `{"@id": "https://ror.org/04ksd4g47"}` |
| `email` | `str` | Required. | Email address of the person. | `ichiro@example.com` |
| `telephone` | `str` | Optional. | Phone number of the person. Hyphen can be used as a separator. | `03-0000-0000` |

## License
A license granted to the data.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be URL of the license. | `https://www.apache.org/licenses/LICENSE-2.0` |
| `name` | `str` | Required. | Name of the license. | `Apache License 2.0` |
| `description` | `str` | Optional. | Description of the license. | `the licensed defined by Apache Software Foundation` |

## RepositoryObject
A repository where the research data is managed in
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be URI of the repository. If it is URL and free to access, DOI link is recommended. | `https://doi.org/xxxxxxxx` |
| `name` | `str` | Required. | Indicates a name of the repository. | `Gakunin RDM` |
| `description` | `str` | Optional. | Indicates a description of the repository. | `Repository managed by NII.` |

## DataDownload
Downloadable dataset from the research project.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be a reachable URL. | `https://zenodo.org/record/example` |
| `description` | `str` | Optional. | Indicates a description of the download. | `All data set is available from this URL as a zip file.` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the download file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `uploadDate` | `str` | Optional. | MUST be a string in ISO 8601 date format. Indicates the date when this data set was uploaded to this site. | `2022-12-01` |

## HostingInstitution
An organization that has responsibility of managing research data.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the URL of the organization. ROR ID is recommended. | `https://ror.org/04ksd4g47` |
| `name` | `str` | Required. | Name of the organization. | `National Institute of Informatics` |
| `description` | `str` | Optional. | Description of the organization. | `Japan's only general academic research institution seeking to create future value in the new discipline of informatics.` |
| `address` | `str` | Required. | Physical address of the organization. | `2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430` |

## ContactPoint
A contact information.
| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be email with the prefix `#mailto:` or be phone number with the prefix `#callto:`. | `#mailto:contact@example.com` |
| `name` | `str` | Required. | Name of a person or a department in charge of managing data set. | `Sample Inc., Open-Science department, data management unit` |
| `email` | `str` | Required either email or telephone (described in the next section). | Email address as contact information. | `contact@example.com` |
| `telephone` | `str` | Required either email (described in the previous section) or telephone. | Phone number as contact information. | `03-0000-0000` |
