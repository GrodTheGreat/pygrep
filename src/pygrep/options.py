from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from pygrep.errors import UsageError


class ColorWhen(StrEnum):
    ALWAYS = "always"
    NEVER = "never"
    AUTO = "auto"


@dataclass
class Options:
    show_version: bool
    is_basic: bool
    is_extended: bool
    only_matches: bool
    is_recursive: bool
    color: ColorWhen
    show_debug: bool
    pattern: str
    files: list[str]


class ArgParser:
    def __init__(self, args: Iterable[str]) -> None:
        self._args = args
        self._show_version = False
        self._is_basic = True
        self._is_extended = False
        self._only_matches = False
        self._is_recursive = False
        self._color = ColorWhen.NEVER
        self._show_debug = False

    def parse(self) -> Options:
        positionals = []
        options_done = False
        for arg in self._args:
            if options_done or arg == "-" or not arg.startswith("-"):
                positionals.append(arg)
            elif arg == "--":
                options_done = True
            elif arg.startswith("--"):
                self._parse_long(arg)
            else:
                self._parse_short(arg)
        if self._show_version:
            return Options(
                self._show_version,
                self._is_basic,
                self._is_extended,
                self._only_matches,
                self._is_recursive,
                self._color,
                self._show_debug,
                "",
                [],
            )
        if len(positionals) == 0:
            raise UsageError()
        pattern = positionals[0]
        files = positionals[1:]
        if not files:
            files = ["."] if self._is_recursive else ["-"]
        return Options(
            self._show_version,
            self._is_basic,
            self._is_extended,
            self._only_matches,
            self._is_recursive,
            self._color,
            self._show_debug,
            pattern,
            files,
        )

    def _parse_long(self, arg: str) -> None:
        key, _, value = arg.partition("=")
        match key:
            case "--version":
                self._show_version = True
            case "--basic-regexp":
                self._is_basic = True
            case "--extended-regexp":
                self._is_extended = True
            case "--only-matching":
                self._only_matches = True
            case "--recursive":
                self._is_recursive = True
            case "--color":
                self._color = ColorWhen.AUTO if not value else self._parse_color(value)
            case "--debug":
                self._show_debug = True
            case _:
                raise UsageError(f"unrecognized option '{arg}'")

    def _parse_short(self, arg: str) -> None:
        for character in arg[1:]:
            match character:
                case "E":
                    self._is_extended = True
                case "G":
                    self._is_basic = True
                case "o":
                    self._only_matches = True
                case "r":
                    self._is_recursive = True
                case _:
                    raise UsageError(f"invalid option -- {character}")

    @staticmethod
    def _parse_color(when: str) -> ColorWhen:
        match when:
            case "always":
                return ColorWhen.ALWAYS
            case "never":
                return ColorWhen.NEVER
            case "auto":
                return ColorWhen.AUTO
            case _:
                raise UsageError("unknown --color option")
