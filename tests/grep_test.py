from collections.abc import Iterable
from io import StringIO

import pytest

from pygrep.environment import Environment
from pygrep.grep import Grep


def highlight(text: str) -> str:
    return f"\033[01;31m{text}\033[m"


CASES = [
    pytest.param(args, stdin, code, out, err, id=name)
    for args, stdin, code, out, err, name in [
        (["a"], "a\n", 0, "a\n", "", "bre-single-character"),
        (["-E", "a"], "a\n", 0, "a\n", "", "ere-single-character"),
        ([r"\d"], "3\nfoo101\n", 0, "3\nfoo101\n", "", "bre-match-digits"),  # check
        ([r"\d"], "c\nArt\n", 1, "", "", "bre-match-digits-fail"),  # check
        (
            [r"\w"],
            "alpha_num3ric\nfoo101\n",
            0,
            "alpha_num3ric\nfoo101\n",
            "",
            "bre-match-words",
        ),  # check
        ([r"\w"], "$!?\n", 1, "", "", "bre-match-words-fail"),  # check
        (["-E", r"\d"], "3\nfoo101\n", 0, "3\nfoo101\n", "", "ere-match-digits"),
        (["-E", r"\d"], "c\nArt\n", 1, "", "", "ere-match-digits-fail"),
        (
            ["-E", r"\w"],
            "alpha_num3ric\nfoo101\n",
            0,
            "alpha_num3ric\nfoo101\n",
            "",
            "ere-match-words",
        ),
        (["-E", r"\w"], "$!?\n", 1, "", "", "ere-match-words-fail"),
        (
            ["[abc]"],
            "apple\ncab\n",
            0,
            "apple\ncab\n",
            "",
            "bre-positive-character-group",
        ),
        (
            ["[abc]"],
            "apple\ncab\n",
            0,
            "apple\ncab\n",
            "",
            "bre-positive-character-group",
        ),
        (["[abc]"], "dog\n", 1, "", "", "bre-positive-character-group-fail"),
        (["[^abc]"], "cat\n", 0, "cat\n", "", "bre-negative-character-group"),
        (["[^abc]"], "cab\n", 1, "", "", "bre-negative-character-group-fail"),
        (
            ["-E", "[abc]"],
            "apple\ncab\n",
            0,
            "apple\ncab\n",
            "",
            "ere-positive-character-group",
        ),
        (["-E", "[abc]"], "dog\n", 1, "", "", "ere-positive-character-group-fail"),
        (["-E", "[^abc]"], "cat\n", 0, "cat\n", "", "ere-negative-character-group"),
        (["-E", "[^abc]"], "cab\n", 1, "", "", "ere-negative-character-group-fail"),
        (
            [r"\d\d\d apples"],
            "I got 100 apples from the store\n",
            0,
            "I got 100 apples from the store\n",
            "",
            "bre-combining-character-classes",
        ),  # check
        (
            [r"\d\d\d apples"],
            "I got 1 apples from the store\n",
            1,
            "",
            "",
            "bre-combining-character-classes-fail",
        ),  # check
        (
            ["-E", r"\d\d\d apples"],
            "I got 100 apples from the store\n",
            0,
            "I got 100 apples from the store\n",
            "",
            "ere-combining-character-classes",
        ),
        (
            ["-E", r"\d\d\d apples"],
            "I got 1 apples from the store\n",
            1,
            "",
            "",
            "ere-combining-character-classes-fail",
        ),
        (["^log"], "log\nlogs\n", 0, "log\nlogs\n", "", "bre-start-of-string-anchor"),
        (["^log"], "slog\n", 1, "", "", "bre-start-of-string-anchor-fail"),
        (["dog$"], "dog\nhotdog\n", 0, "dog\nhotdog\n", "", "bre-end-of-string-anchor"),
        (["dog$"], "dogs\n", 1, "", "", "bre-end-of-string-anchor-fail"),
        (
            ["-E", "^log"],
            "log\nlogs\n",
            0,
            "log\nlogs\n",
            "",
            "ere-start-of-string-anchor",
        ),
        (["-E", "^log"], "slog\n", 1, "", "", "ere-start-of-string-anchor-fail"),
        (
            ["-E", "dog$"],
            "dog\nhotdog\n",
            0,
            "dog\nhotdog\n",
            "",
            "ere-end-of-string-anchor",
        ),
        (["-E", "dog$"], "dogs\n", 1, "", "", "ere-end-of-string-anchor-fail"),
        ([r"ca\+ts"], "cats\ncaats\n", 0, "cats\ncaats\n", "", "bre-match-one-or-more"),
        ([r"ca\+ts"], "cts\n", 1, "", "", "bre-match-one-or-more-fail"),
        ([r"dogs\?"], "dog\ndogs\n", 0, "dog\ndogs\n", "", "bre-match-zero-or-one"),
        ([r"dogs\?"], "cats\n", 1, "", "", "bre-match-zero-or-one-fail"),
        (
            ["-E", "ca+ts"],
            "cats\ncaats\n",
            0,
            "cats\ncaats\n",
            "",
            "ere-match-one-or-more",
        ),
        (["-E", "ca+ts"], "cts\n", 1, "", "", "ere-match-one-or-more-fail"),
        (["-E", "dogs?"], "dog\ndogs\n", 0, "dog\ndogs\n", "", "ere-match-zero-or-one"),
        (["-E", "dogs?"], "cats\n", 1, "", "", "ere-match-zero-or-one-fail"),
        (["d.g"], "dog\ndag\nd9g\n", 0, "dog\ndag\nd9g\n", "", "bre-wildcard"),
        (["d.g"], "cog\ndg\n", 1, "", "", "bre-wildcard-fail"),
        (["-E", "d.g"], "dog\ndag\nd9g\n", 0, "dog\ndag\nd9g\n", "", "ere-wildcard"),
        (["-E", "d.g"], "cog\ndg\n", 1, "", "", "ere-wildcard-fail"),
        (
            [r"\(cat\|dog\)"],
            "cat\ndog\ndoghouse\n",
            0,
            "cat\ndog\ndoghouse\n",
            "",
            "bre-alternation",
        ),
        ([r"\(cat\|dog\)"], "apple\n", 1, "", "", "bre-alternation-fail"),
        (
            ["-E", "(cat|dog)"],
            "cat\ndog\ndoghouse\n",
            0,
            "cat\ndog\ndoghouse\n",
            "",
            "ere-alternation",
        ),
        (["-E", "(cat|dog)"], "apple\n", 1, "", "", "ere-alternation-fail"),
        (["ca*t"], "ct\ncaaat\n", 0, "ct\ncaaat\n", "", "bre-match-zero-or-more"),
        (["ca*t"], "dog\n", 1, "", "", "bre-match-zero-or-more-fail"),
        (["-E", "ca*t"], "ct\ncaaat\n", 0, "ct\ncaaat\n", "", "match-zero-or-more"),
        (["-E", "ca*t"], "dog\n", 1, "", "", "match-zero-or-more-fail"),
        ([r"ca\{3\}t"], "caaat\n", 0, "caaat\n", "", "bre-match-exactly-n"),
        ([r"ca\{3\}t"], "caat\ncaaaat\n", 1, "", "", "bre-match-exactly-n-fail"),
        (
            [r"ca\{2,\}t"],
            "caat\ncaaaaaat\n",
            0,
            "caat\ncaaaaaat\n",
            "",
            "bre-match-n-or-more",
        ),
        ([r"ca\{2,\}t"], "cat\n", 1, "", "", "bre-match-n-or-more-fail"),
        (
            [r"ca\{2,4\}t"],
            "caat\ncaaat\ncaaaat\n",
            0,
            "caat\ncaaat\ncaaaat\n",
            "",
            "bre-match-n-to-m",
        ),
        ([r"ca\{2,4\}t"], "caaaaat\n", 1, "", "", "bre-match-n-to-m-fail"),
        (["-E", "ca{3}t"], "caaat\n", 0, "caaat\n", "", "ere-match-exactly-n"),
        (["-E", "ca{3}t"], "caat\ncaaaat\n", 1, "", "", "ere-match-exactly-n-fail"),
        (
            ["-E", "ca{2,}t"],
            "caat\ncaaaaaat\n",
            0,
            "caat\ncaaaaaat\n",
            "",
            "ere-match-n-or-more",
        ),
        (["-E", "ca{2,}t"], "cat\n", 1, "", "", "ere-match-n-or-more-fail"),
        (
            ["-E", "ca{2,4}t"],
            "caat\ncaaat\ncaaaat\n",
            0,
            "caat\ncaaat\ncaaaat\n",
            "",
            "ere-match-n-to-m",
        ),
        (["-E", "ca{2,4}t"], "caaaaat\n", 1, "", "", "ere-match-n-to-m-fail"),
        (
            [r"\(cat\) and \1"],
            "cat and cat\n",
            0,
            "cat and cat\n",
            "",
            "bre-single-backreference",
        ),
        (
            [r"\(cat\) and \1"],
            "cat and dog\n",
            1,
            "",
            "",
            "bre-single-backreference-fail",
        ),
        (
            [r"\(\d\+\) \(\w\+\) and \1 \2"],
            "3 red and 3 red\n",
            0,
            "3 red and 3 red\n",
            "",
            "bre-multiple-backreferences",
        ),  # check
        (
            [r"\(\d\+\) \(\w\+\) and \1 \2"],
            "3 red and 4 red\n3 red and 3 blue\n",
            1,
            "",
            "",
            "bre-multiple-backreferences-fail",
        ),  # check
        (
            [r"\(\(dog\)-\2\)"],
            "dog-dog\n",
            0,
            "dog-dog\n",
            "",
            "bre-nested-backreferences",
        ),
        (
            ["-E", r"(cat) and \1"],
            "cat and cat\n",
            0,
            "cat and cat\n",
            "",
            "ere-single-backreference",
        ),
        (
            ["-E", r"(cat) and \1"],
            "cat and dog\n",
            1,
            "",
            "",
            "ere-single-backreference-fail",
        ),
        (
            ["-E", r"(\d+) (\w+) and \1 \2"],
            "3 red and 3 red\n",
            0,
            "3 red and 3 red\n",
            "",
            "ere-multiple-backreferences",
        ),
        (
            ["-E", r"(\d+) (\w+) and \1 \2"],
            "3 red and 4 red\n3 red and 3 blue\n",
            1,
            "",
            "",
            "ere-multiple-backreferences-fail",
        ),
        (
            ["-E", r"((dog)-\2)"],
            "dog-dog\n",
            0,
            "dog-dog\n",
            "",
            "ere-nested-backreferences",
        ),
        (
            [r"\d"],
            "line1\nline_two\nline3\n",
            0,
            "line1\nline3\n",
            "",
            "bre-prints-only-matching-lines",
        ),  # check
        (
            ["-E", r"\d"],
            "line1\nline_two\nline3\n",
            0,
            "line1\nline3\n",
            "",
            "ere-prints-only-matching-lines",
        ),
        (["-o", "cow"], "I have one cow\n", 0, "cow\n", "", "bre-only-matches"),
        (
            ["-o", r"\d"],
            "The king had 10 children\n",
            0,
            "1\n0\n",
            "",
            "bre-only-matches-multiple",
        ),  # check
        (
            ["-o", r"\d"],
            "Line1: 10\nLine2: 42\n",
            0,
            "1\n1\n0\n2\n4\n2\n",
            "",
            "bre-only-matches-multiple-lines",
        ),  # check
        (["-E", "-o", "cow"], "I have one cow\n", 0, "cow\n", "", "ere-only-matches"),
        (
            ["-E", "-o", r"\d"],
            "The king had 10 children\n",
            0,
            "1\n0\n",
            "",
            "ere-only-matches-multiple",
        ),
        (
            ["-E", "-o", r"\d"],
            "Line1: 10\nLine2: 42\n",
            0,
            "1\n1\n0\n2\n4\n2\n",
            "",
            "ere-only-matches-multiple-lines",
        ),
        (
            ["--color=always", r"\d"],
            "I have 3 apples\n",
            0,
            f"I have {highlight('3')} apples\n",
            "",
            "bre-highlight-single-match",
        ),  # check
        (
            ["--color=always", r"\(dogs\|cats\)"],
            "dogs and cats are pets\n",
            0,
            f"{highlight('dogs')} and {highlight('cats')} are pets\n",
            "",
            "bre-highlight-multiple-matches",
        ),
        (
            ["--color=always", r"\(dogs\|cats\)"],
            "dogs and cats are pets\ndogs are nice\n",
            0,
            f"{highlight('dogs')} and {highlight('cats')} are pets\n{highlight('dogs')} are nice\n",
            "",
            "bre-highlight-multiple-matches-multiple-lines",
        ),
        (
            ["-E", "--color=always", r"\d"],
            "I have 3 apples\n",
            0,
            f"I have {highlight('3')} apples\n",
            "",
            "ere-highlight-single-match",
        ),
        (
            ["-E", "--color=always", "(dogs|cats)"],
            "dogs and cats are pets\n",
            0,
            f"{highlight('dogs')} and {highlight('cats')} are pets\n",
            "",
            "ere-highlight-multiple-matches",
        ),
        (
            ["-E", "--color=always", "(dogs|cats)"],
            "dogs and cats are pets\ndogs are nice\n",
            0,
            f"{highlight('dogs')} and {highlight('cats')} are pets\n{highlight('dogs')} are nice\n",
            "",
            "ere-highlight-multiple-matches-multiple-lines",
        ),
    ]
]


def run(*args: str, stdin: str = "") -> tuple[int, str, str]:
    out = StringIO()
    err = StringIO()
    code = Grep(Environment(args, StringIO(stdin), out, err, False)).run()
    return code, out.getvalue(), err.getvalue()


@pytest.mark.parametrize(("args", "stdin", "code", "out", "err"), CASES)
def test_grep(args: Iterable[str], stdin: str, code: int, out: str, err: str) -> None:
    assert run(*args, stdin=stdin) == (code, out, err)
