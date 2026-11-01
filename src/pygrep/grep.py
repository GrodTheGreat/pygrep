from pygrep.config import Config
from pygrep.engine import RegexSyntaxError
from pygrep.environment import Environment
from pygrep.errors import UsageError
from pygrep.formatter import Formatter
from pygrep.matcher import Matcher
from pygrep.options import ArgParser, ColorWhen, Options
from pygrep.walker import Source, SourceErr, SourceWalker


def resolve_options(opts: Options, env: Environment) -> Config:
    show_debug = opts.show_debug
    show_paths = len(opts.files) > 1 or opts.is_recursive
    is_recursive = opts.is_recursive
    match opts.color:
        case ColorWhen.ALWAYS:
            show_color = True
        case ColorWhen.AUTO:
            show_color = env.isatty
        case _:
            show_color = False
    return Config(show_debug, show_paths, show_color, opts.only_matches, is_recursive)


class Grep:
    name = "pygrep"

    def __init__(self, env: Environment) -> None:
        self._env = env

    def run(self) -> int:
        parser = ArgParser(self._env.args)
        try:
            opts = parser.parse()
        except UsageError as exc:
            self._handle_usage_error(exc)
            return 2
        if opts.show_version:
            self._env.stdout.write(f"{self.name} (placeholder text) 0.0.0-GlassGrep\n")
            return 0
        cfg = resolve_options(opts, self._env)
        try:
            matcher = Matcher.compile(opts.pattern, opts.is_extended)
        except RegexSyntaxError as exc:
            self._handle_syntax_error(exc, cfg.show_debug)
            return 2

        if cfg.show_debug:
            self._handle_debug(matcher)
        walker = SourceWalker(opts.files, self._env, cfg)
        formatter = Formatter(cfg)
        had_match = False
        had_error = False
        for source in walker.walk():
            match source:
                case Source(path, reader):
                    for raw in reader:
                        line = raw.rstrip("\n")
                        matches = matcher.findall(line)
                        if not matches:
                            continue
                        had_match = True
                        self._env.stdout.write(
                            formatter.format_matches(path, line, matches)
                        )
                case SourceErr(path, exc):
                    had_error = True
                    self._env.stderr.write(formatter.format_os_error(path, exc))
        self._env.stdout.flush()
        self._env.stderr.flush()
        if had_error:
            return 2
        return 0 if had_match else 1

    def _handle_debug(self, matcher: Matcher) -> None:
        self._env.stderr.write(matcher.dmp)
        self._env.stderr.write("\n")
        self._env.stderr.write(matcher.dis)
        self._env.stderr.write("\n")

    def _handle_usage_error(self, exc: UsageError) -> None:
        if exc.message:
            self._env.stderr.write(f"{Grep.name}: {exc.message}")
        self._env.stderr.write(
            f"usage: {Grep.name} [-Eor] [--color=when] [pattern] [file ...]\n"
        )

    def _handle_syntax_error(self, exc: RegexSyntaxError, show_debug: bool) -> None:
        self._env.stderr.write(f"{Grep.name}: {exc.message}")
        if show_debug:
            self._env.stderr.write(f" {exc.pattern} pos: {exc.position}")
        self._env.stderr.write("\n")
        self._env.stderr.flush()
