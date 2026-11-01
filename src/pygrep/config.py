from dataclasses import dataclass


@dataclass
class Config:
    show_debug: bool
    show_paths: bool
    show_color: bool
    only_matches: bool
    is_recursive: bool
