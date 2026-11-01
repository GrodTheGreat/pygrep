from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class Quantity:
    low: int
    high: int | None


@dataclass
class EmptyNode: ...


@dataclass
class CharacterNode:
    value: str


@dataclass
class WildcardNode: ...


@dataclass
class GroupNode:
    node: AstNode
    num: int


@dataclass
class CharacterClassNode:
    negated: bool
    ranges: list[tuple[str, str]]


@dataclass
class BackReferenceNode:
    group: int


@dataclass
class StartOfLineNode: ...


@dataclass
class EndOfLineNode: ...


@dataclass
class ConcatenationNode:
    items: list[AstNode]


@dataclass
class RepeatNode:
    node: AstNode
    low: int
    high: int | None


@dataclass
class AlternationNode:
    expressions: list[AstNode]


AstNode: TypeAlias = (
    EmptyNode
    | CharacterNode
    | WildcardNode
    | GroupNode
    | CharacterClassNode
    | BackReferenceNode
    | StartOfLineNode
    | EndOfLineNode
    | ConcatenationNode
    | RepeatNode
    | AlternationNode
)


@dataclass
class RegexAst:
    node: AstNode
    num_groups: int
