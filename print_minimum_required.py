#!/usr/bin/env python3
"""
recursively print cmake_mimimum_required(VERSION)
"""

from __future__ import annotations
import cmake_file_api
import argparse
from pprint import pprint

p = argparse.ArgumentParser()
p.add_argument("source_dir", help="Top level source directory of CMake project")
P = p.parse_args()

cmake = cmake_file_api.Cmake(P.source_dir)
codemodel = cmake.get_codemodel()

minver: dict[str, str] = {}
for config in codemodel["configurations"]:
    for cd in config["directories"]:
        minver[cd["source"]] = cd["minimumCMakeVersion"]["string"]

pprint(minver)
