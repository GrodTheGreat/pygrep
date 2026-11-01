import os
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import TextIO

from pygrep.config import Config
from pygrep.environment import Environment


@dataclass
class Source:
    path: str
    reader: TextIO


@dataclass
class SourceErr:
    path: str
    exc: OSError


class SourceWalker:
    def __init__(self, paths: Sequence[str], env: Environment, config: Config) -> None:
        self.stack = [*paths]
        self.is_recursive = config.is_recursive
        self.stdin = env.stdin

    def walk(self) -> Iterable[Source | SourceErr]:
        while self.stack:
            path = self.stack.pop()
            if path == "-":
                yield Source("(standard input)", self.stdin)
            elif os.path.isdir(path) and self.is_recursive:
                self._recurse(path)
            else:
                try:
                    with open(path, "r") as reader:
                        yield Source(path, reader)
                except OSError as exc:
                    yield SourceErr(path, exc)

    def _recurse(self, path: str) -> None:  # TODO better name?
        # TODO handle walk errors
        for dirpath, dirnames, filenames in os.walk(path):
            # the real grep doesn't sort at all, but this makes output deterministic
            dirnames.sort()
            for name in sorted(filenames):
                self.stack.append(os.path.join(dirpath, name))
