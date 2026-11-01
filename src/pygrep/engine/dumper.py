from collections.abc import Iterable
from io import StringIO
from typing import assert_never

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


def dump(ast: RegexAst) -> str:
    builder = StringIO()
    _dump_node(builder, ast.node, 0)
    builder.write("\n")
    return builder.getvalue()


def _dump_node(builder: StringIO, node: AstNode, depth: int) -> None:
    builder.write("  " * depth)
    match node:
        case EmptyNode():
            builder.write("(empty)")
        case CharacterNode(value):
            builder.write(f"(character {value})")
        case GroupNode(node, group):
            _dump_group(builder, node, group, depth)
        case CharacterClassNode(negated, ranges):
            _dump_character_class(builder, negated, ranges)
        case WildcardNode():
            builder.write("(wild)")
        case BackReferenceNode(group):
            builder.write(f"(backref {group})")
        case StartOfLineNode():
            builder.write("(sol)")
        case EndOfLineNode():
            builder.write("(eol)")
        case RepeatNode(node, low, high):
            _dump_repeat(builder, node, low, high, depth)
        case ConcatenationNode(items):
            _dump_concat(builder, items, depth)
        case AlternationNode(expressions):
            _dump_alt(builder, expressions, depth)
        case _:
            assert_never(node)


def _dump_alt(builder: StringIO, expressions: Iterable[AstNode], depth: int) -> None:
    builder.write("(alt")
    for expression in expressions:
        builder.write("\n")
        _dump_node(builder, expression, depth + 1)
    builder.write(")")


def _dump_concat(builder: StringIO, items: Iterable[AstNode], depth: int) -> None:
    builder.write("(concat")
    for item in items:
        builder.write("\n")
        _dump_node(builder, item, depth + 1)
    builder.write(")")


def _dump_repeat(
    builder: StringIO, node: AstNode, low: int, high: int | None, depth: int
) -> None:
    builder.write(f"(repeat {low} {high if high is not None else 'unbounded'}\n")
    _dump_node(builder, node, depth + 1)
    builder.write(")")


def _dump_character_class(
    builder: StringIO, negated: bool, ranges: Iterable[tuple[str, str]]
) -> None:
    builder.write("(character-class ")
    if negated:
        builder.write("neg ")
    for low, high in ranges:
        if low == high:
            builder.write(low)
        else:
            builder.write(f"{low}-{high}")
    builder.write(")")


def _dump_group(builder: StringIO, node, num, depth: int) -> None:
    builder.write(f"(group {num}\n")
    _dump_node(builder, node, depth + 1)
    builder.write(")")
