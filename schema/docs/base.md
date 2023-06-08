# NII-DG: Schema: base

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## File
A file included in the research project, such as a text file, script file, or images.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root directory or an absolute URI that is directly downloadable. If the file originates outside the repository, @id SHOULD allow for simple retrieval (e.g., HTTP GET), including redirections and HTTP/HTTPS authentication. RO-Crate metadata (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. | Denotes the file name. | `setting.txt` |
| `contentSize` | `str` | Required. | MUST be an integer representing the file size, suffixed with `B` for bytes. Other units like "KB", "MB", "GB", "TB", and "PB" may also be used if necessary. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be a MIME type, excluding any "x-" prefix. Specifies the file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL link to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is sourced from outside the RO-Crate Root. | Indicates the date the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |

## Dataset
A folder containing files included in the research project.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root (as stated in the identifier property of RootDataEntity) or an absolute URI. MUST end with `/`. This indicates the path to the directory. | `config/` |
| `name` | `str` | Required. | Denotes the directory name. | `config` |
| `url` | `str` | Optional. | MUST be a direct URL link to the directory. | `https://github.com/username/repository/directory` |

## Organization
An entity associated with the research project, such as a university, research institution, or funding agency.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the URL representing the organization. Use of ROR ID is recommended. | `https://ror.org/04ksd4g47` |
| `name` | `str` | Required. | The official name of the organization. | `National Institute of Informatics` |
| `alias` | `str` | Optional. | An alternative or abbreviated name for the organization. | `NII` |
| `description` | `str` | Optional. | A brief description of the organization. | `Japan's only comprehensive research institution striving to innovate in the field of informatics.` |

## Person
An individual contributing to the research project, such as a researcher.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be a URL representing the individual. Use of ORCID ID is recommended. | `https://orcid.org/0000-0001-2345-6789` |
| `name` | `str` | Required. | The full name of the person. MUST follow the format of first name followed by family name. | `Ichiro Suzuki` |
| `alias` | `str` | Optional. | An alternative or abbreviated name for the person. | `S. Ichiro` |
| `affiliation` | `Organization` | Required. | The organization to which the person is affiliated. MUST be a dictionary containing the @id of the Organization entity. | `{"@id": "https://ror.org/04ksd4g47"}` |
| `email` | `str` | Required. | The email address of the person. | `ichiro@example.com` |
| `telephone` | `str` | Optional. | The phone number of the person. Hyphens can be used as separators. | `03-0000-0000` |

## License
A license applied to the dataset.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the URL representing the license. | `https://www.apache.org/licenses/LICENSE-2.0` |
| `name` | `str` | Required. | The official name of the license. | `Apache License 2.0` |
| `description` | `str` | Optional. | A brief explanation of the license. | `The license as defined by the Apache Software Foundation.` |

## RepositoryObject
A repository in which the research data is stored and managed.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the URI of the repository. If accessible via URL, use of DOI link is recommended. | `https://doi.org/xxxxxxxx` |
| `name` | `str` | Required. | The name of the repository. | `Gakunin RDM` |
| `description` | `str` | Optional. | A brief summary of the repository. | `A repository managed by NII.` |

## DataDownload
A downloadable dataset associated with the research project.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be an accessible URL. | `https://zenodo.org/record/example` |
| `description` | `str` | Optional. | A brief explanation about the download. | `All dataset available at this URL as a zip file.` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the downloadable file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `uploadDate` | `str` | Optional. | MUST be in ISO 8601 date format. Indicates the date when the dataset was uploaded to this site. | `2022-12-01` |

## HostingInstitution
An organization tasked with managing research data.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be the URL of the organization. Use of ROR ID is recommended. | `https://ror.org/04ksd4g47` |
| `name` | `str` | Required. | The official name of the organization. | `National Institute of Informatics` |
| `description` | `str` | Optional. | A brief overview of the organization. | `Japan's premier academic research institution striving to pioneer new fields in informatics.` |
| `address` | `str` | Required. | The physical location of the organization. | `2-1-2 Hitotsubashi, Chiyoda-ku, Tokyo, Japan, 101-8430` |

## ContactPoint
Contact information details.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be an email prefixed with `#mailto:` or a phone number prefixed with `#callto:`. | `#mailto:contact@example.com` |
| `name` | `str` | Required. | The name of the person or department responsible for data set management. | `Sample Inc., Open-Science department, data management unit` |
| `email` | `str` | Either email or telephone is required (see following section for telephone). | The email address for contacting the responsible party. | `contact@example.com` |
| `telephone` | `str` | Either email (as described in previous section) or telephone is required. | The telephone number for contacting the responsible party. | `03-0000-0000` |
