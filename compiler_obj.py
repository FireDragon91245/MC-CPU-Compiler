from enum import Enum


class MacroTypes(Enum):
    LABEL = 1
    VARIABLE = 2
    MEMORY_ADDRESS = 3
    NUMBER = 4
    REGISTER = 5


class MemoryManagementType(Enum):
    STATIC_INCREMENTAL = 1
    AUTO_STATIC_INCREMENTAL = 2
    STATIC_BALANCED = 3
    AUTO_STATIC_BALANCED = 4
    EXPLICIT = 5


class Macro:

    def __init__(self, macro_opener: str, macro_closer: str, macro_args: list[MacroTypes], macro_top: list[str], macro_bottom: list[str], complex_macro: bool) -> object:
        self.complex_macro = complex_macro
        self.macro_bottom = macro_bottom
        self.macro_top = macro_top
        self.macro_args = macro_args
        self.macro_closer = macro_closer
        self.macro_opener = macro_opener
