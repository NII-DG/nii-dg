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
    if dmp_f is None:
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


def add_entities_to_crate(crate:NIIROCrate) -> None:
    crate.set_publisheddate()

    key_func = {
        "project_name": crate.set_project_name,
        "funding_agency":crate.set_funder,
        "repository":crate.set_repo,
        "research_field":crate.set_field,
        "e-Rad_project_id":crate.set_erad,
        "license":crate.set_license,
        "affiliation":crate.set_affiliations,
        "creator":crate.set_creators
        }
    funcs = {k: v for k, v in key_func.items() if k in crate.dmp}
    for k, v in funcs.items():
        if crate.dmp.get(k) is not None:
            v(crate.dmp.get(k))
    
    crate.set_dmplist()