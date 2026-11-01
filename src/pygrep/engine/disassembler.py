from collections.abc import Iterable
from io import StringIO
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


def disassemble(program: Program) -> str:
    builder = StringIO()
    for i, instruction in enumerate(program.instructions):
        builder.write(f"{i:04d} ")
        _disassemble_instruction(builder, instruction)
        builder.write("\n")
    dis = builder.getvalue()
    builder.close()
    return dis


def _disassemble_instruction(builder: StringIO, instruction: Instruction) -> None:
    match instruction:
        case MatchInstruction():
            builder.write("MATCH")
        case SaveInstruction(slot):
            builder.write(f"SAVE {slot}")
        case JumpInstruction(to):
            builder.write(f"JUMP {to}")
        case SplitInstruction(first, second):
            builder.write(f"SPLIT {first} {second}")
        case ProgressInstruction(slot):
            builder.write(f"PROGRESS {slot}")
        case CharacterInstruction(value):
            builder.write(f"CHARACTER {value}")
        case WildcardInstruction():
            builder.write("WILD")
        case CharacterClassInstruction(negated, ranges):
            _disassemble_character_class(builder, negated, ranges)
        case BackReferenceInstruction(group):
            builder.write(f"BACKREF {group}")
        case StartOfLineInstruction():
            builder.write("SOL")
        case EndOfLineInstruction():
            builder.write("EOL")
        case _:
            assert_never(instruction)


def _disassemble_character_class(
    builder: StringIO, negated: bool, ranges: Iterable[tuple[str, str]]
) -> None:
    builder.write("CCLASS ")
    if negated:
        builder.write("NEG ")
    for rng in ranges:
        if rng[0] == rng[1]:
            builder.write(rng[0])
        else:
            builder.write(f"{rng[0]}-{rng[1]}")
