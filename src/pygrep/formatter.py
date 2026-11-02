from collections.abc import Iterable
from typing import Literal

from pygrep.config import Config
from pygrep.engine import Match, RegexSyntaxError
from pygrep.errors import UsageError

COLOR_START: Literal["\033[01;31m"] = "\033[01;31m"
COLOR_END: Literal["\033[m"] = "\033[m"


# TODO: This isn't good yet. Want to split the main grep loop from IO/formatting
#  concerns, but seems to be fairly cross cutting. Need to come up with a better solution...
class Formatter:
    name = "pygrep"

    def __init__(self, config: Config) -> None:
        self.show_color = config.show_color
        self.only_matches = config.only_matches
        self.show_path = config.show_paths
        self.show_debug = config.show_debug

    def version(self) -> str:
        return f"{Formatter.name} (placeholder text) 0.0.0-GlassGrep\n"

    def format_syntax_error(self, exc: RegexSyntaxError) -> str:
        txt = f"{Formatter.name}: {exc.message}"
        if self.show_debug:
            txt += f" {exc.pattern} pos: {exc.position}"
        return txt + "\n"

    def format_usage_error(self, exc: UsageError) -> str:
        txt = ""
        if exc.message:
            txt += f"{Formatter.name}: {exc.message}\n"
        txt += f"usage: {Formatter.name} [-Eor] [--color=when] [pattern] [file ...]\n"
        return txt

    def format_os_error(self, path: str, exc: OSError) -> str:
        return f"{Formatter.name}: {path}: {exc.strerror}\n"

    def format_matches(
        self,
        path: str,
        line: str,
        matches: Iterable[Match],
    ) -> str:
        if self.only_matches:
            return self._format_only_matches(path, line, matches)
        else:
            return self._format_matches_full(path, line, matches)

    def _format_matches_full(
        self,
        path: str,
        line: str,
        matches: Iterable[Match],
    ) -> str:
        txt = self._prefix(path)
        end = 0
        for match in matches:
            text = self._highlight(line[match.start : match.end])
            txt += f"{line[end : match.start]}{text}"
            end = match.end
        return txt + line[end:] + "\n"

    def _format_only_matches(
        self, path: str, line: str, matches: Iterable[Match]
    ) -> str:
        txt = ""
        for match in matches:
            if match.start == match.end:
                continue
            txt += self._prefix(path)
            text = line[match.start : match.end]
            txt += f"{self._highlight(text)}\n"
        return txt

    def _highlight(self, text: str) -> str:
        if self.show_color:
            return f"{COLOR_START}{text}{COLOR_END}"
        else:
            return text

    def _prefix(self, path: str) -> str:
        return f"{path}:" if self.show_path else ""
