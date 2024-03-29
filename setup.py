#!/usr/bin/env python3
# coding: utf-8
import importlib
import importlib.util
from pathlib import Path

from setuptools import setup

spec = importlib.util.spec_from_file_location("module_info", "./nii_dg/module_info.py")
nii_dg_module_info = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(nii_dg_module_info)  # type: ignore
GH_REF = nii_dg_module_info.GH_REF

BASE_DIR: Path = Path(__file__).parent.resolve()
LONG_DESCRIPTION: Path = BASE_DIR.joinpath("README.md")


setup(
    name="nii_dg",
    version=GH_REF,
    description="NII Data Governance",
    long_description=LONG_DESCRIPTION.open(mode="r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="NII",
    url="https://github.com/NII-DG/nii-dg",
    license="Apache2.0",
    python_requires=">=3.8",
    platforms="any",
    packages=["nii_dg", "nii_dg.schema"],
    package_data={"nii_dg": ["nii_dg/schema/*.yml"]},
    include_package_data=True,
    install_requires=[
        "flask",
        "pyyaml",
        "waitress",
    ],
    extras_require={
        "tests": [
            "coverage",
            "flake8",
            "isort",
            "mypy",
            "pytest",
            "types-Flask",
            "types-PyYAML",
            "types-waitress",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
