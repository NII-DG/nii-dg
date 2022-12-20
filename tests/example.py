#!/usr/bin/env python3
# coding: utf-8

from pprint import pprint

from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import Dataset, File
from nii_dg.schema.ginfork import File as GinFile


def main() -> None:
    ro_crate = ROCrate()
    file_1 = File("./data/file_1.txt")
    file_2 = File("./data/file_2.txt")
    gin_file = GinFile("./data/file_3.txt")
    dataset = Dataset("./data")
    dataset["hasPart"] = [file_1, file_2, gin_file]
    ro_crate.add(file_1, file_2, gin_file, dataset)
    pprint(ro_crate.as_jsonld())


if __name__ == "__main__":
    main()

"""
{
  '@context': 'https://w3id.org/ro/crate/1.1/context',
    '@graph': [{
      '@context': 'https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/RootDataEntity.json',
      '@id': './',
      '@type': 'Dataset',
      'hasPart': [{ '@id': './data/file_1.txt' },
      { '@id': './data/file_2.txt' },
      { '@id': './data' }]
    },
    {
      '@id': 'ro-crate-metadata.json',
      '@type': 'CreativeWork',
      'about': { '@id': './' },
      'conformsTo': { '@id': 'https://w3id.org/ro/crate/1.1' }
    },
    {
      '@context': 'https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/File.json',
      '@id': './data/file_1.txt',
      '@type': 'File'
    },
    {
      '@context': 'https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/File.json',
      '@id': './data/file_2.txt',
      '@type': 'File'
    },
    {
      '@context': 'https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Dataset.json',
      '@id': './data',
      '@type': 'Dataset',
      'hasPart': [{ '@id': './data/file_1.txt' },
      { '@id': './data/file_2.txt' }]
    }]
}
"""
