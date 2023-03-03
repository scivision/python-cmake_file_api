from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
import shutil
import subprocess
import logging
import argparse
import json
from pprint import pprint


@dataclass
class Cmake():

    cmake_exe: str
    source_dir: Path
    build_dir: Path

    def __init__(self, source_dir: str | None = None, build_dir: str | None = None):

        if cmake_exe := shutil.which("cmake"):
            self.cmake_exe = cmake_exe
        else:
            raise FileNotFoundError('CMake executable not found')

        self.source_dir = Path(source_dir).expanduser().resolve() if source_dir else Path.cwd()

        self.build_dir = Path(build_dir).expanduser().resolve() if build_dir else self.source_dir / 'build'

    def generate(self) -> None:
        """
        CMake Generate
        """

        wopts: list[str] = []

        gen_cmd = [self.cmake_exe] + wopts

        gen_cmd += [f"-S{self.source_dir}",  f"-B{self.build_dir}"]
        subprocess.check_call(gen_cmd)


    def get_cache(self) -> dict[str, str]:
        api_dir = self.build_dir / '.cmake/api/v1'
        query_dir = api_dir / 'query'
        query_dir.mkdir(parents=True, exist_ok=True)

        # request CMake Cache info
        (query_dir / 'cache-v2').touch()

        resp_dir = api_dir / 'reply'
        indices = sorted(resp_dir.glob('index-*.json'), reverse=True)
        if indices:
            index_fn = indices[0]
            if (self.source_dir / 'CMakeLists.txt').stat().st_mtime > index_fn.stat().st_mtime:
                logging.info('CMakeLists.txt modified after response index, regenerating')
                self.generate()
                index_fn = sorted(resp_dir.glob('index-*.json'), reverse=True)[0]
        else:
            logging.info('CMake run for first generation')
            self.generate()
            index_fn = sorted(resp_dir.glob('index-*.json'), reverse=True)[0]

        index = json.loads(index_fn.read_text())
        cache_fn = resp_dir / index['reply']['cache-v2']['jsonFile']

        cmakecache = json.loads(cache_fn.read_text())
        cache = {entry['name']: entry['value'] for entry in cmakecache['entries']}

        return cache


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('source_dir', help="Top level source directory of CMake project")
    P = p.parse_args()

    cmake = Cmake(P.source_dir)
    cache = cmake.get_cache()

    pprint(cache)
