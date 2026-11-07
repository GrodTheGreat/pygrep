from collections.abc import Callable
from typing import assert_never

from pygrep.engine import Match
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
    RegexAst,
    RepeatNode,
    StartOfLineNode,
    WildcardNode,
)

Slots = tuple[int, ...]
Continuation = Callable[[int, Slots], Match | None]


class TreeWalker:
    def __init__(self, ast: RegexAst) -> None:
        self._ast = ast

    def execute(self, candidate: str, start: int) -> Match | None:
        def _done(sp: int, _: Slots) -> Match | None:
            return Match(candidate[start:sp], start, sp)

        return self._execute_node(
            self._ast.node, candidate, start, (-1,) * self._ast.num_groups * 2, _done
        )

    def _execute_node(
        self, node: AstNode, candidate: str, sp: int, slots: Slots, cont: Continuation
    ) -> Match | None:
        match node:
            case AlternationNode(expressions):
                for expression in expressions:
                    res = self._execute_node(expression, candidate, sp, slots, cont)
                    if res:
                        return res
                return None
            case ConcatenationNode(items):

                def step(i: int, sp: int, slots: Slots) -> Match | None:
                    if i == len(items):
                        return cont(sp, slots)

                    def next_step(sp: int, slots: Slots) -> Match | None:
                        return step(i + 1, sp, slots)

                    return self._execute_node(items[i], candidate, sp, slots, next_step)

                return step(0, sp, slots)
            case RepeatNode(node, low, high):

                def attempt(i: int, sp: int, slots: Slots) -> Match | None:
                    if high is None or i < high:

                        def next_attempt(
                            next_sp: int, next_slots: Slots
                        ) -> Match | None:
                            if next_sp == sp:
                                return cont(next_sp, next_slots)
                            return attempt(i + 1, next_sp, next_slots)

                        res = self._execute_node(
                            node, candidate, sp, slots, next_attempt
                        )
                        if res:
                            return res
                    if i >= low:
                        return cont(sp, slots)
                    return None

                return attempt(0, sp, slots)
            case EmptyNode():
                return cont(sp, slots)
            case CharacterNode(value):
                if sp >= len(candidate) or candidate[sp] != value:
                    return None
                return cont(sp + 1, slots)
            case CharacterClassNode(negated, ranges):
                if sp >= len(candidate):
                    return None
                in_range = any(r[0] <= candidate[sp] <= r[1] for r in ranges)
                if negated == in_range:
                    return None
                return cont(sp + 1, slots)
            case GroupNode(node, num):
                slots = list(slots)
                slots[num * 2] = sp

                def next_step(next_sp: int, next_slots: Slots) -> Match | None:
                    slots = list(next_slots)
                    slots[num * 2 + 1] = next_sp
                    return cont(next_sp, tuple(slots))

                return self._execute_node(node, candidate, sp, tuple(slots), next_step)
            case WildcardNode():
                if sp >= len(candidate) or candidate[sp] == "\n":
                    return None
                return cont(sp + 1, slots)
            case BackReferenceNode(group):
                start = slots[group * 2]
                end = slots[group * 2 + 1]
                if start == -1 or end == -1:
                    return None
                substring = candidate[start:end]
                sublen = len(substring)
                if (
                    sp + sublen > len(candidate)
                    or candidate[sp : sp + sublen] != substring
                ):
                    return None
                return cont(sp + sublen, slots)
            case StartOfLineNode():
                if sp != 0:
                    return None
                return cont(sp, slots)
            case EndOfLineNode():
                if sp != len(candidate):
                    return None
                return cont(sp, slots)
            case _:
                assert_never(node)
