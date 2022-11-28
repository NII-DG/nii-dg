import json
import os
import jsonschema
from nii_dg.model.rocrate import NIIROCrate


class ValidationError(Exception):
    pass

def read_dmp(path):
    with open(path) as f:
        metadata = json.load(f)
    return metadata


def set_dmp_format(dict):
    dmp_f = dict.get('dmp_format')
    if (dmp_f is None):
        raise ValidationError('property "dmp_format" is missing.')
    dmp_f = dmp_f.replace(' ', '_')

    input_schema = '/' + dmp_f + '_schema.json'
    with open(os.path.dirname(__file__) +input_schema) as js:
        schema = json.load(js)

    error_messages = []
    v = jsonschema.Draft202012Validator(schema)
    for error in v.iter_errors(dict):
        error_messages.append(error.message)

    if len(error_messages) > 0:
        raise ValidationError('\n'.join(error_messages))

    return NIIROCrate(dict, dmp_f)


def generate_rocrate(dmp_path=None, dir_path=None):
    if dmp_path is None:
        dmp_path = input('dmp.json path:')
    metadata = read_dmp(dmp_path)

    crate = set_dmp_format(metadata)
    crate.set_project_name()
    crate.set_publisheddate()
    crate.set_funder()
    crate.set_repo()
    crate.set_license()
    crate.set_erad()
    crate.set_creators()
    crate.set_affiliations()
    crate.set_field()
    crate.set_grdm()
    crate.overwrite()
    # crate.load_data_dir(dir_path)
    roc = crate.generate()

    with open('ro-crate-metadata.json', 'w') as f:
        json.dump(roc, f, indent=4)
