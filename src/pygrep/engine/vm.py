from dataclasses import dataclass
from typing import assert_never

from pygrep.engine.instructions import (
    BackReferenceInstruction,
    CharacterClassInstruction,
    CharacterInstruction,
    EndOfLineInstruction,
    JumpInstruction,
    MatchInstruction,
    Program,
    ProgressInstruction,
    SaveInstruction,
    SplitInstruction,
    StartOfLineInstruction,
    WildcardInstruction,
)
from pygrep.engine.match import Match


@dataclass
class Branch:
    instruction_pointer: int
    string_pointer: int
    slots: tuple[int, ...]


# TODO: Real grep does leftmost/longest match. This backtracking engine will give you that
#  but will always run slow. A Perl engine version would return on the first match. Add as an option?
# TODO: Backtracking works and gives back refs, but is very slow. Add an interface for things like
#  a pyke vm if pattern is fully regular.
class VirtualMachine:
    def __init__(self, program: Program) -> None:
        self._program = program
        self._call_stack: list[Branch] = []

    def execute(self, candidate: str, start: int) -> Match | None:
        best: Match | None = None
        self._call_stack.clear()
        self._call_stack.append(Branch(0, start, (-1,) * self._program.num_slots))
        while self._call_stack:
            branch = self._call_stack.pop()
            match = self._execute_thread(branch, candidate)
            if match and (best is None or best.end < match.end):
                best = match
        return best

    def _execute_thread(self, branch: Branch, candidate: str) -> Match | None:
        ip = branch.instruction_pointer
        sp = branch.string_pointer
        slots = list(branch.slots)
        while True:
            instruction = self._program.instructions[ip]
            match instruction:
                case MatchInstruction():
                    start = slots[0]
                    end = slots[1]
                    assert start >= 0 and end >= 0, (
                        "match reached without saving slots 0 and 1"
                    )
                    return Match(candidate[start:end], start, end)
                case CharacterInstruction(value):
                    if sp >= len(candidate) or candidate[sp] != value:
                        return None
                    ip += 1
                    sp += 1
                case WildcardInstruction():
                    if sp >= len(candidate) or candidate[sp] == "\n":
                        return None
                    ip += 1
                    sp += 1
                case CharacterClassInstruction(negated, ranges):
                    if sp >= len(candidate):
                        return None
                    in_range = any(
                        low <= candidate[sp] <= high for (low, high) in ranges
                    )
                    if negated == in_range:
                        return None
                    ip += 1
                    sp += 1
                case BackReferenceInstruction(group):
                    start = slots[group * 2]
                    end = slots[group * 2 + 1]
                    if start == -1 or end == -1:
                        return None
                    substring = candidate[start:end]
                    if sp + len(substring) > len(candidate):
                        return None
                    if candidate[sp : sp + len(substring)] != substring:
                        return None
                    ip += 1
                    sp += len(substring)
                case StartOfLineInstruction():
                    if sp != 0:
                        return None
                    ip += 1
                case EndOfLineInstruction():
                    if sp != len(candidate):
                        return None
                    ip += 1
                case SaveInstruction(slot):
                    slots[slot] = sp
                    ip += 1
                case SplitInstruction(first, second):
                    # TODO: Definitely a better way to do the slots then a full convert to tuple <-> list...
                    self._call_stack.append(Branch(second, sp, tuple(slots)))
                    ip = first
                case JumpInstruction(to):
                    ip = to
                case ProgressInstruction(slot):
                    if sp == slots[slot]:
                        return None
                    ip += 1
                case _:
                    assert_never(instruction)
