from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class MatchInstruction: ...


@dataclass
class SaveInstruction:
    slot: int


@dataclass
class JumpInstruction:
    to: int


@dataclass
class SplitInstruction:
    first: int
    second: int


@dataclass
class ProgressInstruction:
    slot: int


@dataclass
class CharacterInstruction:
    value: str


@dataclass
class WildcardInstruction: ...


@dataclass
class CharacterClassInstruction:
    negated: bool
    ranges: list[tuple[str, str]]


@dataclass
class BackReferenceInstruction:
    group: int


@dataclass
class StartOfLineInstruction: ...


@dataclass
class EndOfLineInstruction: ...


Instruction: TypeAlias = (
    MatchInstruction
    | SaveInstruction
    | JumpInstruction
    | SplitInstruction
    | ProgressInstruction
    | CharacterInstruction
    | WildcardInstruction
    | CharacterClassInstruction
    | BackReferenceInstruction
    | StartOfLineInstruction
    | EndOfLineInstruction
)


@dataclass
class Program:
    instructions: list[Instruction]
    num_slots: int
    num_groups: int
