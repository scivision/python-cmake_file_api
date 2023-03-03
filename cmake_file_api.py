"""
Complete standalone example of querying CMake file-api
* cache
* codemodel (targets, files, configurations)

https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html
"""

from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import shutil
import subprocess
import argparse
import json
from pprint import pprint


@dataclass
class Cmake:

    cmake_exe: str
    source_dir: Path
    build_dir: Path
    api_dir: Path
    query_dir: Path
    resp_dir: Path

    def __init__(self, source_dir: str | None = None, build_dir: str | None = None):

        if cmake_exe := shutil.which("cmake"):
            self.cmake_exe = cmake_exe
        else:
            raise FileNotFoundError("CMake executable not found")

        self.source_dir = Path(source_dir).expanduser().resolve() if source_dir else Path.cwd()

        self.build_dir = Path(build_dir).expanduser().resolve() if build_dir else self.source_dir / "build"

        self.api_dir = self.build_dir / ".cmake/api/v1"
        self.query_dir = self.api_dir / "query"
        self.query_dir.mkdir(parents=True, exist_ok=True)
        self.resp_dir = self.api_dir / "reply"

    def generate(self) -> None:
        """
        CMake Generate
        """

        wopts: list[str] = []

        gen_cmd = [self.cmake_exe] + wopts

        gen_cmd += [f"-S{self.source_dir}", f"-B{self.build_dir}"]
        subprocess.check_call(gen_cmd)

    def get_index(self) -> dict[str, str]:
        """get index of CMake file-api reply files"""

        self.generate()
        indices = sorted(self.resp_dir.glob("index-*.json"))

        return json.loads(indices[-1].read_text())

    def get_cache(self) -> dict[str, str]:
        """get CMake cache as dict"""

        (self.query_dir / "cache-v2").touch()

        index = self.get_index()
        cache_fn = self.resp_dir / index["reply"]["cache-v2"]["jsonFile"]

        return json.loads(cache_fn.read_text())

    def get_codemodel(self) -> dict[str, str]:
        """get CMake codemodel as dict"""

        (self.query_dir / "codemodel-v2").touch()

        index = self.get_index()
        codemodel_fn = self.resp_dir / index["reply"]["codemodel-v2"]["jsonFile"]

        codemodel = json.loads(codemodel_fn.read_text())

        return codemodel

    def get_target_jsonFiles(self) -> list[str]:
        """get list of target JSON index files"""

        codemodel = self.get_codemodel()
        targets = [target["jsonFile"] for target in codemodel["configurations"][0]["targets"]]

        return targets


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("source_dir", help="Top level source directory of CMake project")
    P = p.parse_args()

    cmake = Cmake(P.source_dir)

    # cache = cmake.get_cache()
    # pprint(cache)

    # codemodel = cmake.get_codemodel()
    # pprint(codemodel)

    for file in cmake.get_target_jsonFiles():
        target = json.loads((cmake.resp_dir / file).read_text())
        pprint(target)
