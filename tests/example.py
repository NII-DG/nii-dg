#!/usr/bin/env python3
# coding: utf-8

from pprint import pprint

from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset, File, Organization


def main() -> None:
    ro_crate = ROCrate()
    ro_crate.root["name"] = "example research project"
    funder = Organization("https://www.nii.ac.jp/", {"name": "National Institute of Informatics"})
    ro_crate.root["funder"] = [funder]
    file_1 = File("./data/file_1.txt", {"name": "Sample File", "contentSize": "156GB"})
    dataset = Dataset("./data/", {"name": "Sample Folder"})

    ro_crate.add(file_1, dataset, funder)
    pprint(ro_crate.as_jsonld())


if __name__ == "__main__":
    main()

"""
{'@context': 'https://w3id.org/ro/crate/1.1/context',
 '@graph': [{'@context': 'https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/RootDataEntity.json',
             '@id': './',
             '@type': 'Dataset',
             'dateCreated': '2022-12-27T07:57:27.362+00:00',
             'funder': [{'@id': 'https://www.nii.ac.jp/'}],
             'hasPart': [{'@id': './data/file_1.txt'}, {'@id': './data/'}],
             'name': 'example research project'},
            {'@id': 'ro-crate-metadata.json',
             '@type': 'CreativeWork',
             'about': {'@id': './'},
             'conformsTo': {'@id': 'https://w3id.org/ro/crate/1.1'}},
            {'@context': 'https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/File.json',
             '@id': './data/file_1.txt',
             '@type': 'File',
             'contentSize': '156GB',
             'name': 'Sample File'},
            {'@context': 'https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Dataset.json',
             '@id': './data/',
             '@type': 'Dataset',
             'name': 'Sample Folder'},
            {'@context': 'https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Organization.json',
             '@id': 'https://www.nii.ac.jp/',
             '@type': 'Organization',
             'name': 'National Institute of Informatics'}]}
"""
