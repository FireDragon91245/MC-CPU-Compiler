from enum import Enum


class MacroTypes(Enum):
    LABEL = 1
    VARIABLE = 2
    MEMORY_ADDRESS = 3
    NUMBER = 4
    REGISTER = 5


class Macro:

    def __init__(self, macro_opener: str, macro_closer: str, macro_args: list[MacroTypes], macro_top: list[str],
                 macro_bottom: list[str], complex_macro: bool) -> None:
        self.complex_macro = complex_macro
        self.macro_bottom = macro_bottom
        self.macro_top = macro_top
        self.macro_args = macro_args
        self.macro_closer = macro_closer
        self.macro_opener = macro_opener
        self.macro_no = 0


class CompilerArgs:

    def __init__(self, target_lang: str, mem_size: int, memory_blocks: int, stack_size: int,
                 register_count: int) -> None:
        self.register_count = register_count
        self.memory_blocks = memory_blocks
        self.mem_size = mem_size
        self.target_lang = target_lang
        self.stack_size = stack_size


class LanguageTarget:

    def transpile(self, compile_lines: list[str], rom_instructions: list[(int, int, int)], args: CompilerArgs):
        pass
