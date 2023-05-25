# Example for the nii-dg Library

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

These commands generate files named `invalid_crate1.json` and `invalid_crate2.json`. Both files are invalid RO-Crates.

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
 <cao.Person https://en.wikipedia.org/wiki/Ichiro_Suzuki>,
 <base.RepositoryObject https://example.com/repository>,
 <cao.DMP #dmp:1>,
 <cao.DMPMetadata #CAO-DMP>]
```

## Example 3: Validating a RO-Crate

This example demonstrates the process of validating a RO-Crate.

```bash
$ python3 validate_crate.py sample_crate.json
# no output
```

If an invalid or "broken" RO-Crate is loaded, the validation process will fail.

```bash
$ python3 validate_crate.py invalid_crate1.json
Traceback (most recent call last):
  File "validate_crate.py", line 30, in <module>
    main()
  File "validate_crate.py", line 26, in main
    validate_crate(crate)
  File "validate_crate.py", line 12, in validate_crate
    crate.validate()
  File "/home/ubuntu/git/github.com/NII-DG/nii-dg/nii_dg/ro_crate.py", line 317, in validate
    raise crate_error
nii_dg.error.CrateValidationError: CrateValidationError: Errors occurred in validate() for entities:

- EntityError: Errors occurred in <cao.Person https://example.com/person>: {'@id': 'Failed to access the URL.'}
- EntityError: Errors occurred in <ginfork.GinMonitoring #ginmonitoring>: {'experimentPackageList': "Required Dataset entity is missing; @id '[PosixPath('experiments/exp1/source'), PosixPath('experiments/exp1/input_data'), PosixPath('experiments/exp1/output_data')]'."}

$ python3 validate_crate.py invalid_crate2.json
Traceback (most recent call last):
  File "validate_crate.py", line 31, in <module>
    main()
  File "validate_crate.py", line 27, in main
    validate_crate(crate)
  File "validate_crate.py", line 12, in validate_crate
    crate.check_props()
  File "/home/ubuntu/git/github.com/NII-DG/nii-dg/nii_dg/ro_crate.py", line 298, in check_props
    raise crate_error
nii_dg.error.CrateCheckPropsError: CrateCheckPropsError: Errors occurred in check_props() for entities:

- EntityError: Errors occurred in <cao.File file_1.txt>: {'contentSize': 'The type of this property MUST be str.'}
```
