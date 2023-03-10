"""
Complete standalone example of querying CMake file-api
* cache
* codemodel (targets, files, configurations)

https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html
"""

from __future__ import annotations
from pathlib import Path
import typing as T
from dataclasses import dataclass
import shutil
import subprocess
import json
import sys

if sys.version_info < (3, 8):
    raise RuntimeError("Python >= 3.8 required")


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

        self.source_dir = Path(source_dir).expanduser().resolve(strict=True) if source_dir else Path.cwd()

        self.build_dir = (
            Path(build_dir).expanduser().resolve(strict=False) if build_dir else self.source_dir / "build"
        )

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

    def get_reply(self) -> dict[str, dict[str, str]]:
        """get index of CMake file-api reply files"""

        self.generate()
        indices = sorted(self.resp_dir.glob("index-*.json"))

        return json.loads(indices[-1].read_text())["reply"]

    def get_cache(self) -> dict[str, dict[str, str]]:
        """get CMake cache as dict"""

        (self.query_dir / "cache-v2").touch()

        cache_fn = self.resp_dir / self.get_reply()["cache-v2"]["jsonFile"]

        return json.loads(cache_fn.read_text())

    def get_codemodel(self) -> dict[str, list[dict]]:
        """get CMake codemodel as dict"""

        (self.query_dir / "codemodel-v2").touch()

        codemodel_fn = self.resp_dir / self.get_reply()["codemodel-v2"]["jsonFile"]

        return json.loads(codemodel_fn.read_text())

    def get_target_jsonFiles(self) -> T.Iterator[str]:
        """get target JSON index files"""

        return (target["jsonFile"] for target in self.get_codemodel()["configurations"][0]["targets"])
