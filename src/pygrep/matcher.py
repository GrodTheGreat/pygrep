from pygrep.engine import Match
from pygrep.engine.compiler import Compiler
from pygrep.engine.disassembler import disassemble
from pygrep.engine.dumper import dump
from pygrep.engine.parser import BasicParser, ExtendedParser
from pygrep.engine.tree_walker import TreeWalker
from pygrep.engine.vm import VirtualMachine


class Matcher:
    def __init__(
        self, vm: VirtualMachine, dmp: str, dis: str, walker: TreeWalker
    ) -> None:
        self.vm = vm
        self.dmp = dmp  # TODO: maybe better to use callbacks?
        self.dis = dis  # TODO: maybe better to use callbacks?
        self.walker = walker

    @classmethod
    def compile(cls, pattern: str, is_extended: bool) -> Matcher:
        if is_extended:
            parser = ExtendedParser(pattern)
        else:
            parser = BasicParser(pattern)
        ast = parser.parse()
        dmp = dump(ast)
        compiler = Compiler(ast)
        program = compiler.compile()
        dis = disassemble(program)
        return cls(VirtualMachine(program), dmp, dis, TreeWalker(ast))

    def test(self, candidate: str) -> bool:
        return self.search(candidate) is not None

    def match(self, candidate: str) -> Match | None:
        return self.vm.execute(candidate, 0)

    def search(self, candidate: str) -> Match | None:
        for i in range(len(candidate) + 1):
            match = self.vm.execute(candidate, i)
            if match:
                return match
        return None

    def findall(self, candidate: str) -> list[Match]:
        matches = []
        i = 0
        while i <= len(candidate):
            match = self.walker.execute(candidate, i)
            if match:
                matches.append(match)
                i = match.end if match.end != i else i + 1
            else:
                i += 1
        return matches
