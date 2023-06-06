#!/usr/bin/env python3
# coding: utf-8

import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List

from nii_dg.entity import (ContextualEntity, DataEntity, DefaultEntity,
                           RootDataEntity)
from nii_dg.ro_crate import ROCrate

# === load test module ===

here = Path(__file__).parent.resolve()
test_module_path = here.joinpath("../example/package_crate.py").resolve()
spec = importlib.util.spec_from_file_location("package_crate", test_module_path)
test_module = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(test_module)  # type: ignore

package_crate = test_module.package_crate

# === test ===

sample_crate_jsonld_path = here.joinpath("../example/sample_crate.json").resolve()
with sample_crate_jsonld_path.open("r", encoding="utf-8") as f:
    expect_jsonld = json.load(f)


def compare_jsonld_graph(
    expect: List[Dict[str, Any]], actual: List[Dict[str, Any]]
) -> None:
    """\
    exclude:
        - @context
            - cause of changing depends on version of module
        - datePublished
            - cause of changing
    """
    expect_dict = {f"{ent['@id']}_{ent['@type']}": ent for ent in expect}
    actual_dict = {f"{ent['@id']}_{ent['@type']}": ent for ent in actual}
    assert expect_dict.keys() == actual_dict.keys()

    for id_type in expect_dict.keys():
        expect_ent = expect_dict[id_type]
        actual_ent = actual_dict[id_type]
        assert expect_ent.keys() == actual_ent.keys()
        for key in expect_ent.keys():
            if key in ["@context", "datePublished"]:
                continue
            assert expect_ent[key] == actual_ent[key]


def test_package_crate() -> None:
    ro_crate = package_crate()

    assert isinstance(ro_crate, ROCrate)
    for default_ent in ro_crate.default_entities:
        assert isinstance(default_ent, DefaultEntity)
    for data_ent in ro_crate.data_entities:
        assert isinstance(data_ent, DataEntity)
    for contextual_ent in ro_crate.contextual_entities:
        assert isinstance(contextual_ent, ContextualEntity)
    assert isinstance(ro_crate.root, RootDataEntity)

    actual_jsonld = ro_crate.as_jsonld()
    assert expect_jsonld["@context"] == actual_jsonld["@context"]
    compare_jsonld_graph(expect_jsonld["@graph"], actual_jsonld["@graph"])
