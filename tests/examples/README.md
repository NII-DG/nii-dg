# Examples for the nii-dg Library

## Example1: Packaging a Research Project as a RO-Crate

This example demonstrates the process of packaging a research project as a RO-Crate.

```bash
$ python3 package_crate.py
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    ...
```

The RO-Crate, which is in JSON-LD format, is output to the standard output. Additionally, a file named `sample_crate.json` is generated as an instance of a standard RO-Crate. The content of this file is identical to the standard output.

For generating a RO-Crate that fails validation, execute the following command:

```bash
$ python3 package_invalid_crate1.py
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    ...

$ python3 package_invalid_crate2.py
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    ...
```

These commands generate files named `broken_crate1.json` and `broken_crate2.json`. Both files are invalid RO-Crates.

## Example 2: Loading a RO-Crate from a JSON-LD File

This example demonstrates the process of loading a RO-Crate from a JSON-LD file.

```bash
$ python3 load_crate.py sample_crate.json
=== Root ===
<Dataset ./>
=== Default ===
[<Dataset ./>, <CreativeWork ro-crate-metadata.json>]
=== Data ===
[<cao.File file_1.txt>]
=== Contextual ===
[<base.HostingInstitution https://www.nii.ac.jp/>,
 <cao.Person https://ja.wikipedia.org/wiki/%E3%82%A4%E3%83%81%E3%83%AD%E3%83%BC>,
 <base.RepositoryObject https://example.com/repository>,
 <cao.DMP #dmp:1>,
 <cao.DMPMetadata #CAO-DMP>]
```

## Example 3: Validating a RO-Crate

This example demonstrates the process of validating a RO-Crate.

```bash
$ python3 validate_crate.py sample_crate.json
```

If an invalid or "broken" RO-Crate is loaded, the validation process will fail.

```bash
$ python3 validate_crate.py broken_crate1.json

$ python3 validate_crate.py broken_crate2.json
```
