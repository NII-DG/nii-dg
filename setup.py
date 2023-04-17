#!/usr/bin/env python3
# coding: utf-8
from pathlib import Path

from setuptools import setup

from .nii_dg.module_info import GH_REF

BASE_DIR: Path = Path(__file__).parent.resolve()
LONG_DESCRIPTION: Path = BASE_DIR.joinpath("README.md")


setup(
    name="nii_dg",
    version=GH_REF,
    description="NII Data Governance",
    long_description=LONG_DESCRIPTION.open(mode="r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="NII",
    python_requires=">=3.7",
    platforms="any",
    packages=["nii_dg", "nii_dg/schema"],
    package_data={"nii_dg": ["schema/*.yml"]},
    install_requires=[
        "flask",
        "pyyaml",
        "waitress",
    ],
    tests_require=[
        "flake8",
        "isort",
        "mypy",
        "pytest",
        "types-PyYAML",
        "types-Flask",
        "types-waitress",
    ],
    extras_require={
        "tests": [
            "flake8",
            "isort",
            "mypy",
            "pytest",
            "types-PyYAML",
            "types-Flask",
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
