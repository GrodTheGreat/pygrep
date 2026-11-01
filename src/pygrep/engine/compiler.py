from collections.abc import Iterable, Sequence
from typing import assert_never

from pygrep.engine.instructions import (
    BackReferenceInstruction,
    CharacterClassInstruction,
    CharacterInstruction,
    EndOfLineInstruction,
    Instruction,
    JumpInstruction,
    MatchInstruction,
    Program,
    ProgressInstruction,
    SaveInstruction,
    SplitInstruction,
    StartOfLineInstruction,
    WildcardInstruction,
)
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

PLACEHOLDER = 0


class Compiler:
    def __init__(self, regex: RegexAst):
        self._regex = regex
        self._instructions: list[Instruction] = []
        self._next_slot = self._regex.num_groups * 2

    def compile(self) -> Program:
        self._instructions = []
        self._instructions.append(SaveInstruction(0))
        self._compile_node(self._regex.node)
        self._instructions.append(SaveInstruction(1))
        self._instructions.append(MatchInstruction())
        return Program(self._instructions, self._next_slot, self._regex.num_groups)

    def _compile_node(self, node: AstNode) -> None:
        match node:
            case EmptyNode():
                return
            case CharacterNode(value):
                self._instructions.append(CharacterInstruction(value))
            case WildcardNode():
                self._instructions.append(WildcardInstruction())
            case CharacterClassNode(negated, ranges):
                self._instructions.append(CharacterClassInstruction(negated, ranges))
            case GroupNode(node, num):
                self._compile_group(node, num)
            case BackReferenceNode(group):
                self._instructions.append(BackReferenceInstruction(group))
            case StartOfLineNode():
                self._instructions.append(StartOfLineInstruction())
            case EndOfLineNode():
                self._instructions.append(EndOfLineInstruction())
            case ConcatenationNode(items):
                self._compile_concatenation(items)
            case RepeatNode(node, low, high):
                self._compile_repeat(node, low, high)
            case AlternationNode(expressions):
                self._compile_alternation(expressions)
            case _:
                assert_never(node)

    def _compile_alternation(self, expressions: Sequence[AstNode]) -> None:
        jump_indexes = []
        for i, expression in enumerate(expressions):
            is_last = i == len(expressions) - 1
            if is_last:
                self._compile_node(expression)
                continue
            self._instructions.append(SplitInstruction(PLACEHOLDER, PLACEHOLDER))
            split_index = len(self._instructions) - 1
            first_index = len(self._instructions)
            self._compile_node(expression)
            self._instructions.append(JumpInstruction(PLACEHOLDER))
            jump_indexes.append(len(self._instructions) - 1)
            self._instructions[split_index] = SplitInstruction(
                first_index, len(self._instructions)
            )
        end = len(self._instructions)
        for index in jump_indexes:
            self._instructions[index] = JumpInstruction(end)

    def _compile_concatenation(self, items: Iterable[AstNode]) -> None:
        for item in items:
            self._compile_node(item)

    def _compile_repeat(self, node: AstNode, low: int, high: int | None) -> None:
        self._compile_repeat_lower(node, low)
        if high is None:
            self._compile_repeat_upper_unbounded(node)
        else:
            self._compile_repeat_upper_bounded(node, high - low)

    def _compile_repeat_lower(self, node: AstNode, times: int) -> None:
        for _ in range(times):
            self._compile_node(node)

    def _compile_repeat_upper_unbounded(self, node: AstNode) -> None:
        start = len(self._instructions)
        self._instructions.append(SplitInstruction(PLACEHOLDER, PLACEHOLDER))
        split_index = len(self._instructions) - 1
        first_index = len(self._instructions)
        slot = self._next_slot
        self._next_slot += 1
        self._instructions.append(SaveInstruction(slot))
        self._compile_node(node)
        self._instructions.append(ProgressInstruction(slot))
        self._instructions.append(JumpInstruction(start))
        self._instructions[split_index] = SplitInstruction(
            first_index, len(self._instructions)
        )

    def _compile_repeat_upper_bounded(self, node: AstNode, times: int) -> None:
        split_indexes = []
        first_indexes = []
        for _ in range(times):
            self._instructions.append(SplitInstruction(PLACEHOLDER, PLACEHOLDER))
            split_indexes.append(len(self._instructions) - 1)
            first_indexes.append(len(self._instructions))
            self._compile_node(node)
        for split_index, first_index in zip(split_indexes, first_indexes):
            self._instructions[split_index] = SplitInstruction(
                first_index, len(self._instructions)
            )

    def _compile_group(self, node: AstNode, num: int) -> None:
        self._instructions.append(SaveInstruction(num * 2))
        self._compile_node(node)
        self._instructions.append(SaveInstruction(num * 2 + 1))
