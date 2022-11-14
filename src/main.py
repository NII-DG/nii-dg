import json
import jsonschema
from model.rocrate import NIIROCrate

class ValidationError(Exception):
    pass

# input file should be json 
def read_dmp(path):
    with open(path) as f:
        metadata = json.load(f)
    return metadata

def set_dmp_format(dict):
    dmp_f = dict.get('dmp_format')
    if (dmp_f is None):
        raise ValidationError('property "dmp_format" is missing.')
    dmp_f = dmp_f.replace(' ','')

    input_schema = dmp_f + '_schema.json'
    with open(input_schema) as js:
        schema = json.load(js)
    
    error_messages = []
    v = jsonschema.Draft202012Validator(schema)
    for error in v.iter_errors(dict):
        error_messages.append(error.message)
    
    if len(error_messages) > 0:
        raise ValidationError('\n'.join(error_messages))

    return NIIROCrate(dict)

def generate_rocrate():
    dmp_path = input('dmp.json path:')
    metadata = read_dmp(dmp_path)

    crate = set_dmp_format(metadata)    
    crate.set_project_name()
    crate.set_funder()
    roc = crate.generate()
    
    with open('ro-crate-metadata.json', 'w') as f:
        json.dump(roc, f, indent = 4)
