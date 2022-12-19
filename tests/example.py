#!/usr/bin/env python3
# coding: utf-8

from pprint import pprint

from nii_dg.ro_crate import ROCrate
from nii_dg.schema import Dataset, File


def main() -> None:
    ro_crate = ROCrate()
    file_1 = File("./data/file_1.txt")
    file_2 = File("./data/file_2.txt")
    dataset = Dataset("./data")
    dataset["hasPart"] = [file_1, file_2]
    ro_crate.add(file_1, file_2, dataset)
    pprint(ro_crate.as_jsonld())


if __name__ == "__main__":
    main()
