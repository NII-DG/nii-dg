import json
import os
<<<<<<< HEAD
from typing import Any
=======
>>>>>>> 23b1b8b... Add github action and update README

import jsonschema

from nii_dg import const
from nii_dg.model.rocrate import NIIROCrate


class ValidationError(Exception):
    pass


<<<<<<< HEAD
def read_dmp(path) -> dict[str, Any]:
=======
def read_dmp(path):
>>>>>>> 23b1b8b... Add github action and update README
    '''
    入力となるJSONをdictとして読む
    '''
    with open(path, encoding="utf-8") as f:
        metadata = json.load(f)
    return metadata


def validate_with_schema(dict_: dict[str, Any]) -> None:
    '''
    JSON-Schemaで入力を検証
    '''
<<<<<<< HEAD
    with open(os.path.dirname(__file__) + "/schema.json", encoding="utf-8") as schemafile:
=======
    with open(os.path.dirname(__file__) + '/schema.json', encoding='utf-8') as schemafile:
>>>>>>> 23b1b8b... Add github action and update README
        schema = json.load(schemafile)

    error_messages = []
    v = jsonschema.Draft202012Validator(schema)
    for error in v.iter_errors(dict_):
        error_messages.append(error.message)

    if len(error_messages) > 0:
        raise ValidationError("\n".join(error_messages))


<<<<<<< HEAD
def check_dmp_format(dict_: dict[str, Any]) -> None:
=======

def check_dmp_format(dict_):
>>>>>>> 23b1b8b... Add github action and update README
    '''
    入力からDMPの形式を抽出
    対応するものか確認
    '''
    dmp_f = dict_.get("dmpFormat")
    if dmp_f is None:
        raise ValidationError("property \"dmpFormat\" is missing.")
    if dmp_f not in const.DMPSTYLES:
        raise ValidationError(f"This library does not yet support {dmp_f} dmp.")


def generate_crate_instance(dict_: dict[str, Any]) -> NIIROCrate:
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
<<<<<<< HEAD
        "projectName": crate.set_project_name,
        "fundingAgency": crate.set_funder,
        "repository": crate.set_repo,
        "researchField": crate.set_field,
        "e-RadProjectId": crate.set_erad,
        "license": crate.set_license,
=======
        "project_name": crate.set_project_name,
        "funding_agency": crate.set_funder,
        "repository": crate.set_repo,
        "research_field": crate.set_field,
        "e-Rad_project_id": crate.set_erad,
        "license": crate.set_license,
        "affiliation": crate.set_affiliations,
>>>>>>> 23b1b8b... Add github action and update README
        "creator": crate.set_creators
    }
    funcs = {k: v for k, v in key_func.items() if k in crate.dmp}
    for k, v in funcs.items():
        if crate.dmp.get(k) is not None:
            v(crate.dmp.get(k))

<<<<<<< HEAD
    if crate.dmp_format == "common_metadata":
=======
    if crate.dmp_format == 'common_metadata':
>>>>>>> 23b1b8b... Add github action and update README
        crate.set_dmp_common()
    else:
        pass  # tbd
