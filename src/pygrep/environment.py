from collections.abc import Iterable
from dataclasses import dataclass
from typing import TextIO


@dataclass
class Environment:
    args: Iterable[str]
    stdin: TextIO
    stdout: TextIO
    stderr: TextIO
    isatty: bool
