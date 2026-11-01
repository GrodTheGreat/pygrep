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


class ExtendedParser(Parser):
    def __init__(self, pattern: str) -> None:
        self._pattern = pattern
        self._current = 0
        self._num_groups = 1
        self._highest_backref = None

    def parse(self) -> RegexAst:
        node = self._alternation()
        if not self._is_at_end():
            self._report_error("parentheses not balanced")
        if (
            self._highest_backref is not None
            and self._highest_backref > self._num_groups
        ):
            self._report_error("invalid backreference number")
        return RegexAst(node, self._num_groups)

    def _alternation(self) -> AstNode:
        first = self._concatenation()
        rest = []
        while not self._is_at_end() and self._match("|"):
            rest.append(self._concatenation())
        if not rest:
            return first
        return AlternationNode([first, *rest])

    def _concatenation(self) -> AstNode:
        items = []
        while not self._is_at_end() and self._peek() != "|" and self._peek() != ")":
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
        match self._peek():
            case "?":
                self._advance()
                return Quantity(0, 1)
            case "+":
                self._advance()
                return Quantity(1, None)
            case "*":
                self._advance()
                return Quantity(0, None)
            case "{":
                return self._bounds()
            case _:
                return None

    def _bounds(self) -> Quantity | None:
        start = self._current
        self._advance()
        low = self._integer()
        had_comma = self._match(",")
        high = self._integer() if had_comma else low
        if low is not None and high is not None and high < low:
            self._report_error("invalid repetition count(s)")
        if self._match("}") and (low is not None or high is not None):
            return Quantity(low if low is not None else 0, high)
        self._current = start
        return None

    def _atom(self) -> AstNode:
        character = self._advance()
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
                self._report_error("repetition operand invalid")
            case _:
                return CharacterNode(character)

    def _escaped(self) -> AstNode:
        if self._is_at_end():
            self._report_error("trailing backslash (\\)")
        character = self._advance()
        shorthand = self._shorthand(character)
        if shorthand:
            return shorthand
        if not character.isdigit() or character == "0":
            return CharacterNode(character)
        self._current -= 1
        group = self._integer()
        assert group is not None, "invalid integer"
        if self._highest_backref is None or group > self._highest_backref:
            self._highest_backref = group
        return BackReferenceNode(group)

    def _character_class(self) -> AstNode:
        negated = self._match("^")
        ranges = []
        while not self._is_at_end() and self._peek() != "]":
            start = self._advance()
            if self._peek() == "-" and self._peek_next() not in ("", "]"):
                self._advance()
                end = self._advance()
                if start > end:
                    self._report_error("invalid character range")
                ranges.append((start, end))
            else:
                ranges.append((start, start))
        self._expect("]", "unclosed character range")
        return CharacterClassNode(negated, ranges)

    def _group(self) -> AstNode:
        num = self._num_groups
        self._num_groups += 1
        node = self._alternation()
        self._expect(")", "parentheses not balanced")
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
        start = self._current
        while self._peek().isdigit():
            self._advance()
        if self._current == start:
            return None
        return int(self._pattern[start : self._current])

    def _is_at_end(self) -> bool:
        return self._current >= len(self._pattern)

    def _peek(self) -> str:
        if self._is_at_end():
            return ""
        return self._pattern[self._current]

    def _peek_next(self) -> str:
        if self._current + 1 >= len(self._pattern):
            return ""
        return self._pattern[self._current + 1]

    def _advance(self) -> str:
        if self._is_at_end():
            return ""
        character = self._pattern[self._current]
        self._current += 1
        return character

    def _match(self, character: str) -> bool:
        if self._peek() != character:
            return False
        self._advance()
        return True

    def _expect(self, character: str, message: str) -> None:
        if not self._match(character):
            self._report_error(message)

    def _report_error(self, message) -> NoReturn:
        raise RegexSyntaxError(message, self._pattern, self._current)


class BasicParser(Parser):
    def __init__(self, pattern: str) -> None:
        self._pattern = pattern
        self._current = 0
        self._num_groups = 1
        self._highest_backref = None

    def parse(self) -> RegexAst:
        ast = self._alternation()
        if not self._is_at_end():
            self._report_error("parentheses not balanced")
        if (
            self._highest_backref is not None
            and self._highest_backref > self._num_groups
        ):
            self._report_error("invalid backreference number")
        return RegexAst(ast, self._num_groups)

    def _alternation(self) -> AstNode:
        first = self._concatenation()
        rest = []
        while not self._is_at_end() and self._matches_escaped("|"):
            rest.append(self._concatenation())
        if not rest:
            return first
        return AlternationNode([first, *rest])

    def _concatenation(self) -> AstNode:
        items = []
        while not self._is_at_end():
            if self._peek() == "\\" and (
                self._peek_next() == "|" or self._peek_next() == ")"
            ):  # TODO can this be expressed more elegantly?
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
        character = self._advance()
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
        if self._is_at_end():
            self._report_error("trailing backslash (\\)")
        character = self._advance()
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
        negated = self._matches("^")
        ranges = []
        while not self._is_at_end() and self._peek() != "]":
            low = self._advance()
            if (
                self._peek() == "-"
                and self._peek_next() != "]"
                and self._peek_next() != ""
            ):
                self._advance()
                high = self._advance()
                if high < low:
                    self._report_error("invalid character range")
                ranges.append((low, high))
            else:
                ranges.append((low, low))
        self._expects("]", "unclosed character range")
        return CharacterClassNode(negated, ranges)

    def _back_reference(self) -> AstNode:
        self._current -= 1
        num = self._integer()
        if num is None:
            self._report_error("invalid back-reference")
        if self._highest_backref is None or self._highest_backref < num:
            self._highest_backref = num
        return BackReferenceNode(num)

    def _quantifier(self) -> Quantity | None:
        if self._is_at_end():
            return None
        if self._peek() == "*":
            self._advance()
            return Quantity(0, None)
        if self._peek() != "\\":
            return None
        match self._peek_next():
            case "?":
                self._advance()
                self._advance()
                return Quantity(0, 1)
            case "+":
                self._advance()
                self._advance()
                return Quantity(1, None)
            case "{":
                return self._bounded()
            case _:
                return None

    def _bounded(self) -> Quantity:
        self._advance()
        self._advance()
        low = self._integer()
        high = self._integer() if self._matches(",") else low
        if low is not None and high is not None and high < low:
            self._report_error("invalid repetition count(s)")
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
        start = self._current
        while not self._is_at_end() and self._peek().isdigit():
            self._advance()
        if self._current == start:
            return None
        return int(self._pattern[start : self._current])

    def _is_at_end(self) -> bool:
        return self._current >= len(self._pattern)

    def _peek(self) -> str:
        if self._is_at_end():
            return ""
        return self._pattern[self._current]

    def _peek_next(self) -> str:
        if self._current + 1 >= len(self._pattern):
            return ""
        return self._pattern[self._current + 1]

    def _advance(self) -> str:
        if self._is_at_end():
            return ""
        character = self._pattern[self._current]
        self._current += 1
        return character

    def _matches(self, character: str) -> bool:
        if self._peek() != character:
            return False
        self._advance()
        return True

    def _matches_escaped(self, character: str) -> bool:
        if self._peek() != "\\" or self._peek_next() != character:
            return False
        self._advance()
        self._advance()
        return True

    def _expects(self, character: str, message: str) -> None:
        if not self._matches(character):
            self._report_error(message)

    def _expects_escaped(self, character: str, message: str) -> None:
        if not self._matches_escaped(character):
            self._report_error(message)

    def _report_error(self, message: str) -> NoReturn:
        raise RegexSyntaxError(message, self._pattern, self._current)
