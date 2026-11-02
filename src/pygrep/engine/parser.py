from typing import NoReturn, Protocol

from pygrep.engine import RegexSyntaxError
from pygrep.engine.nodes import (
    AlternationNode,
    AstNode,
    BackReferenceNode,
    CharacterClassNode,
    CharacterNode,
    ConcatenationNode,
    EmptyNode,
    EndOfLineNode,
    GroupNode,
    Quantity,
    RegexAst,
    RepeatNode,
    StartOfLineNode,
    WildcardNode,
)

DIGIT_RANGE = [("0", "9")]
WORD_RANGE = [("a", "z"), ("A", "Z"), ("0", "9"), ("_", "_")]
SPACE_RANGE = [(" ", " "), ("\t", "\r")]


class Parser(Protocol):
    def parse(self) -> RegexAst: ...


class _Reader:
    def __init__(self, source: str) -> None:
        self._source = source
        self._current = 0

    @property
    def source(self) -> str:
        return self._source

    @property
    def current(self) -> int:
        return self._current

    def seek(self, position: int) -> None:
        self._current = position

    def is_at_end(self) -> bool:
        return self._current >= len(self._source)

    def advance(self) -> str:
        character = self._source[self._current]
        self._current += 1
        return character

    def peek(self) -> str:
        if self.is_at_end():
            return ""
        return self._source[self._current]

    def peek_next(self) -> str:
        if self._current + 1 >= len(self._source):
            return ""
        return self._source[self._current + 1]

    def matches(self, character: str) -> bool:
        if self.is_at_end() or self._source[self._current] != character:
            return False
        self.advance()
        return True

    def expects(self, character: str, message: str) -> None:
        if not self.matches(character):
            self.report(message)

    def report(self, message: str) -> NoReturn:
        raise RegexSyntaxError(message, self._source, self._current)


class ExtendedParser(Parser):
    def __init__(self, pattern: str) -> None:
        self._reader = _Reader(pattern)
        self._num_groups = 1
        self._highest_backref = None

    def parse(self) -> RegexAst:
        ast = self._alternation()
        if not self._reader.is_at_end():
            self._reader.report("parentheses not balanced")
        if (
            self._highest_backref is not None
            and self._highest_backref > self._num_groups
        ):
            self._reader.report("invalid backreference number")
        return RegexAst(ast, self._num_groups)

    def _alternation(self) -> AstNode:
        first = self._concatenation()
        rest = []
        while not self._reader.is_at_end() and self._reader.matches("|"):
            rest.append(self._concatenation())
        if not rest:
            return first
        return AlternationNode([first, *rest])

    def _concatenation(self) -> AstNode:
        items = []
        while (
            not self._reader.is_at_end()
            and self._reader.peek() != "|"
            and self._reader.peek() != ")"
        ):
            items.append(self._repetition())
        if not items:
            return EmptyNode()
        elif len(items) == 1:
            return items[0]
        return ConcatenationNode(items)

    def _repetition(self) -> AstNode:
        node = self._atom()
        quantity = self._quantifier()
        if not quantity:
            return node
        return RepeatNode(node, quantity.low, quantity.high)

    def _quantifier(self) -> Quantity | None:
        match self._reader.peek():
            case "?":
                self._reader.advance()
                return Quantity(0, 1)
            case "+":
                self._reader.advance()
                return Quantity(1, None)
            case "*":
                self._reader.advance()
                return Quantity(0, None)
            case "{":
                return self._bounds()
            case _:
                return None

    def _bounds(self) -> Quantity | None:
        start = self._reader.current
        self._reader.advance()
        low = self._integer()
        had_comma = self._reader.matches(",")
        high = self._integer() if had_comma else low
        if not (self._reader.matches("}") and (low is not None or high is not None)):
            self._reader.seek(start)
            return None
        if low is not None and high is not None and high < low:
            self._reader.report("invalid repetition count(s)")
        if high is not None and high > 255:
            self._reader.report("maximum repetition exceeds 255")
        return Quantity(low if low is not None else 0, high)

    def _atom(self) -> AstNode:
        character = self._reader.advance()
        match character:
            case ".":
                return WildcardNode()
            case "^":
                return StartOfLineNode()
            case "$":
                return EndOfLineNode()
            case "\\":
                return self._escaped()
            case "(":
                return self._group()
            case "[":
                return self._character_class()
            case "?" | "+" | "*":
                self._reader.report("repetition operand invalid")
            case _:
                return CharacterNode(character)

    def _escaped(self) -> AstNode:
        if self._reader.is_at_end():
            self._reader.report("trailing backslash (\\)")
        character = self._reader.advance()
        shorthand = self._shorthand(character)
        if shorthand:
            return shorthand
        if not character.isdigit() or character == "0":
            return CharacterNode(character)
        self._reader.seek(self._reader.current - 1)
        group = self._integer()
        assert group is not None, "invalid integer"
        if self._highest_backref is None or group > self._highest_backref:
            self._highest_backref = group
        return BackReferenceNode(group)

    def _character_class(self) -> AstNode:
        negated = self._reader.matches("^")
        ranges = []
        while not self._reader.is_at_end() and self._reader.peek() != "]":
            start = self._reader.advance()
            if self._reader.peek() == "-" and self._reader.peek_next() not in ("", "]"):
                self._reader.advance()
                end = self._reader.advance()
                if start > end:
                    self._reader.report("invalid character range")
                ranges.append((start, end))
            else:
                ranges.append((start, start))
        self._reader.expects("]", "unclosed character range")
        return CharacterClassNode(negated, ranges)

    def _group(self) -> AstNode:
        num = self._num_groups
        self._num_groups += 1
        node = self._alternation()
        self._reader.expects(")", "parentheses not balanced")
        return GroupNode(node, num)

    @staticmethod
    def _shorthand(character: str) -> AstNode | None:
        match character:
            case "d":
                return CharacterClassNode(False, DIGIT_RANGE)
            case "D":
                return CharacterClassNode(True, DIGIT_RANGE)
            case "w":
                return CharacterClassNode(False, WORD_RANGE)
            case "W":
                return CharacterClassNode(True, WORD_RANGE)
            case "s":
                return CharacterClassNode(False, SPACE_RANGE)
            case "S":
                return CharacterClassNode(True, SPACE_RANGE)
            case _:
                return None

    def _integer(self) -> int | None:
        start = self._reader.current
        while self._reader.peek().isdigit():
            self._reader.advance()
        if self._reader.current == start:
            return None
        return int(self._reader.source[start : self._reader.current])


class BasicParser(Parser):
    def __init__(self, pattern: str) -> None:
        self._reader = _Reader(pattern)
        self._num_groups = 1
        self._highest_backref = None

    def parse(self) -> RegexAst:
        ast = self._alternation()
        if not self._reader.is_at_end():
            self._reader.report("parentheses not balanced")
        if (
            self._highest_backref is not None
            and self._highest_backref > self._num_groups
        ):
            self._reader.report("invalid backreference number")
        return RegexAst(ast, self._num_groups)

    def _alternation(self) -> AstNode:
        first = self._concatenation()
        rest = []
        while not self._reader.is_at_end() and self._matches_escaped("|"):
            rest.append(self._concatenation())
        if not rest:
            return first
        return AlternationNode([first, *rest])

    def _concatenation(self) -> AstNode:
        items = []
        while not self._reader.is_at_end():
            if self._reader.peek() == "\\" and self._reader.peek_next() in "|)":
                break
            items.append(self._repetition())
        match len(items):
            case 0:
                return EmptyNode()
            case 1:
                return items.pop()
            case _:
                return ConcatenationNode(items)

    def _repetition(self) -> AstNode:
        node = self._atom()
        quantity = self._quantifier()
        if not quantity:
            return node
        return RepeatNode(node, quantity.low, quantity.high)

    def _atom(self) -> AstNode:
        character = self._reader.advance()
        match character:
            case ".":
                return WildcardNode()
            case "^":
                return StartOfLineNode()
            case "$":
                return EndOfLineNode()
            case "[":
                return self._character_class()
            case "\\":
                return self._escaped()
            case _:
                return CharacterNode(character)

    def _escaped(self) -> AstNode:
        if self._reader.is_at_end():
            self._reader.report("trailing backslash (\\)")
        character = self._reader.advance()
        short = self._shorthand(character)
        if short:
            return short
        elif character == "(":
            return self._group()
        elif character.isdigit() and character != "0":
            return self._back_reference()
        else:
            return CharacterNode(character)

    def _group(self) -> AstNode:
        num = self._num_groups
        self._num_groups += 1
        node = self._alternation()
        self._expects_escaped(")", "parentheses not balanced")
        return GroupNode(node, num)

    def _character_class(self) -> AstNode:
        negated = self._reader.matches("^")
        ranges = []
        while not self._reader.is_at_end() and self._reader.peek() != "]":
            low = self._reader.advance()
            if (
                self._reader.peek() == "-"
                and self._reader.peek_next() != "]"
                and self._reader.peek_next() != ""
            ):
                self._reader.advance()
                high = self._reader.advance()
                if high < low:
                    self._reader.report("invalid character range")
                ranges.append((low, high))
            else:
                ranges.append((low, low))
        self._reader.expects("]", "unclosed character range")
        return CharacterClassNode(negated, ranges)

    def _back_reference(self) -> AstNode:
        self._reader.seek(self._reader.current - 1)
        num = self._integer()
        if num is None:
            self._reader.report("invalid back-reference")
        if self._highest_backref is None or self._highest_backref < num:
            self._highest_backref = num
        return BackReferenceNode(num)

    def _quantifier(self) -> Quantity | None:
        if self._reader.is_at_end():
            return None
        if self._reader.peek() == "*":
            self._reader.advance()
            return Quantity(0, None)
        if self._reader.peek() != "\\":
            return None
        match self._reader.peek_next():
            case "?":
                self._reader.advance()
                self._reader.advance()
                return Quantity(0, 1)
            case "+":
                self._reader.advance()
                self._reader.advance()
                return Quantity(1, None)
            case "{":
                return self._bounded()
            case _:
                return None

    def _bounded(self) -> Quantity:
        self._reader.advance()
        self._reader.advance()
        low = self._integer()
        high = self._integer() if self._reader.matches(",") else low
        if low is not None and high is not None and high < low:
            self._reader.report("invalid repetition count(s)")
        if high is not None and high > 255:
            self._reader.report("maximum repetition exceeds 255")
        self._expects_escaped("}", "braces not balanced")
        return Quantity(low if low is not None else 0, high)

    @staticmethod
    def _shorthand(character: str) -> AstNode | None:
        match character:
            case "d":  # check
                return CharacterClassNode(False, DIGIT_RANGE)
            case "D":  # check
                return CharacterClassNode(True, DIGIT_RANGE)
            case "w":
                return CharacterClassNode(False, WORD_RANGE)
            case "W":
                return CharacterClassNode(True, WORD_RANGE)
            case "s":
                return CharacterClassNode(False, SPACE_RANGE)
            case "S":
                return CharacterClassNode(True, SPACE_RANGE)
            case _:
                return None

    def _integer(self) -> int | None:
        start = self._reader.current
        while not self._reader.is_at_end() and self._reader.peek().isdigit():
            self._reader.advance()
        if self._reader.current == start:
            return None
        return int(self._reader.source[start : self._reader.current])

    def _matches_escaped(self, character: str) -> bool:
        if self._reader.peek() != "\\" or self._reader.peek_next() != character:
            return False
        self._reader.advance()
        self._reader.advance()
        return True

    def _expects_escaped(self, character: str, message: str) -> None:
        if not self._matches_escaped(character):
            self._reader.report(message)
