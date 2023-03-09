#!/usr/bin/env python3

import cmake_file_api
import argparse
from pprint import pprint

p = argparse.ArgumentParser()
p.add_argument("source_dir", help="Top level source directory of CMake project")
P = p.parse_args()

cmake = cmake_file_api.Cmake(P.source_dir)

cache = cmake.get_cache()
pprint(cache)
