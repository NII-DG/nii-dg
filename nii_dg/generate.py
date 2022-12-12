import json
import os

import jsonschema

from nii_dg import const
from nii_dg.model.rocrate import NIIROCrate


class ValidationError(Exception):
    pass


def read_dmp(path):
    '''
    入力となるJSONをdictとして読む
    '''
    with open(path) as f:
        metadata = json.load(f)
    return metadata


def validate_with_schema(dict_):
    '''
    JSON-Schemaで入力を検証
    '''
    with open(os.path.dirname(__file__) + '/schema.json', encoding='utf-8') as schemafile:
        schema = json.load(schemafile)

    error_messages = []
    v = jsonschema.Draft202012Validator(schema)
    for error in v.iter_errors(dict_):
        error_messages.append(error.message)

    if len(error_messages) > 0:
        raise ValidationError('\n'.join(error_messages))


def check_dmp_format(dict_):
    '''
    入力からDMPの形式を抽出
    対応するものか確認
    '''
    dmp_f = dict_.get('dmpFormat')
    if dmp_f is None:
        raise ValidationError('property "dmpFormat" is missing.')
    if dmp_f not in const.DMPSTYLES:
        raise ValidationError(f'This library does not yet support {dmp_f} dmp.')


def generate_crate_instance(dict_):
    '''
    DMPの形式
    '''
    check_dmp_format(dict_)
    validate_with_schema(dict_)

    return NIIROCrate(dict_)


def add_entities_to_crate(crate: NIIROCrate) -> None:
    '''
    入力JSONのkeyに対して対応するメソッドを実行しコンテキストエンティティを追加
    '''
    crate.set_publisheddate()

    key_func = {
        "projectName": crate.set_project_name,
        "fundingAgency": crate.set_funder,
        "repository": crate.set_repo,
        "researchField": crate.set_field,
        "e-RadProjectId": crate.set_erad,
        "license": crate.set_license,
        "creator": crate.set_creators
    }
    funcs = {k: v for k, v in key_func.items() if k in crate.dmp}
    for k, v in funcs.items():
        if crate.dmp.get(k) is not None:
            v(crate.dmp.get(k))

    if crate.dmp_format == 'common_metadata':
        crate.set_dmp_common()
    else:
        pass  # tbd
