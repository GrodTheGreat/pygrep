from dataclasses import dataclass


@dataclass
class Match:
    value: str
    start: int
    end: int
