#!/usr/bin/env python3
# coding: utf-8

import json

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

    print(json.dumps(ro_crate.as_jsonld(), indent=2))


if __name__ == "__main__":
    main()

"""
{
  "@context": "https://w3id.org/ro/crate/1.1/context",
  "@graph": [
    {
      "@id": "./",
      "@type": "Dataset",
      "hasPart": [
        {
          "@id": "./data/file_1.txt"
        },
        {
          "@id": "./data/"
        }
      ],
      "name": "example research project",
      "funder": [
        {
          "@id": "https://www.nii.ac.jp/"
        }
      ],
      "dateCreated": "2023-01-10T07:19:23.632+00:00",
      "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/RootDataEntity.json"
    },
    {
      "@id": "ro-crate-metadata.json",
      "@type": "CreativeWork",
      "conformsTo": {
        "@id": "https://w3id.org/ro/crate/1.1"
      },
      "about": {
        "@id": "./"
      }
    },
    {
      "@id": "./data/file_1.txt",
      "@type": "File",
      "name": "Sample File",
      "contentSize": "156GB",
      "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/File.json"
    },
    {
      "@id": "./data/",
      "@type": "Dataset",
      "name": "Sample Folder",
      "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Dataset.json"
    },
    {
      "@id": "https://www.nii.ac.jp/",
      "@type": "Organization",
      "name": "National Institute of Informatics",
      "@context": "https://raw.githubusercontent.com/ascade/nii_dg/develop/schema/context/base/Organization.json"
    }
  ]
}
"""
