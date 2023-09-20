from abc import abstractmethod
from enum import Enum
from pathlib import Path
from typing import Type

import regex


class MacroTypes(Enum):
    LABEL = 1
    VARIABLE = 2
    MEMORY_ADDRESS = 3
    NUMBER = 4
    REGISTER = 5
    REGISTER_POINTER = 6
    STRING = 7


class CompilerErrorLevels(Enum):
    INFO = 1
    OK = 2
    WARNING = 3
    ERROR = 4
    NONE = 5

    def is_severity_higher(self, other):
        return self.value > other.value


class Macro:

    def __init__(self, macro_opener: str, macro_closer: str, macro_args: list[MacroTypes], macro_top: list[str],
                 macro_bottom: list[str], complex_macro: bool, generated_macro: bool, macro_generator) -> None:
        self.macro_generator = macro_generator
        self.generated_macro = generated_macro
        self.complex_macro = complex_macro
        self.macro_bottom = macro_bottom
        self.macro_top = macro_top
        self.macro_args = macro_args
        self.macro_closer = macro_closer
        self.macro_opener = macro_opener
        self.macro_no = 0

    def __cmp__(self, other):
        return self.complex_macro == other.complex_macro and self.macro_bottom == other.macro_bottom and\
            self.macro_top == other.macro_top and self.macro_args == other.macro_args and\
            self.macro_closer == other.macro_closer and self.macro_opener == other.macro_opener and\
            self.macro_generator == other.macro_generator and self.generated_macro == other.generated_macro


class CompilerArgs:

    def __init__(self, target_lang: str, mem_size: int, memory_blocks: int, stack_size: int, register_count: int,
                 exit_level: CompilerErrorLevels, out_file: str) -> None:
        self.out_file = out_file
        self.exit_level = exit_level
        self.register_count = register_count
        self.memory_blocks = memory_blocks
        self.mem_size = mem_size
        self.target_lang = target_lang
        self.stack_size = stack_size


class CompilerResult:

    def __init__(self, status: CompilerErrorLevels | None, message: str | None) -> None:
        self.message = message
        self.status = status
        self.messages: list[(CompilerErrorLevels, str)] = []

    @staticmethod
    def ok():
        return CompilerResult(CompilerErrorLevels.OK, "")

    @staticmethod
    def error(message: str):
        return CompilerResult(CompilerErrorLevels.ERROR, message)

    @staticmethod
    def warn(message: str):
        return CompilerResult(CompilerErrorLevels.WARNING, message)

    @staticmethod
    def info(message: str):
        return CompilerResult(CompilerErrorLevels.INFO, message)

    def accumulate(self, other):

        if other.status is None:
            return self
        if other.message_count() == 1:
            if self.status is None:
                self.status = other.status
                self.message = other.message
                return self

            if len(self.messages) == 0:
                self.messages.append((self.status, self.message))

            if other.status.is_severity_higher(self.status):
                self.status = other.status

                self.messages.append((other.status, other.message))
        else:
            for sev, msg in other.messages:
                if self.status is None:
                    self.status = sev
                    self.message = msg
                    continue

                if len(self.messages) == 0:
                    self.messages.append((sev, msg))

                if sev.is_severity_higher(self.status):
                    self.status = sev

                    self.messages.append((sev, msg))
        return self

    def message_count(self) -> int:
        return 1 if len(self.messages) == 0 else len(self.messages)

    def __str__(self) -> str:
        if self.message_count() == 1:
            return f"[{self.status}] {self.message}"
        else:
            res = ""
            for msg in self.messages:
                res += f"[{msg[0]}] {msg[1]}\n"
            return res

    @staticmethod
    def empty():
        return CompilerResult(None, None)

    def not_empty_or_ok(self):
        return self if self.status is not None else self.ok()


class MacroGenerator:
    @staticmethod
    @abstractmethod
    def get_target_language() -> str:
        pass

    @abstractmethod
    def __init__(self, generator_lines: list[str]) -> None:
        pass

    @abstractmethod
    def load_generator(self, args: CompilerArgs, macro: Macro) -> CompilerResult:
        pass

    @abstractmethod
    def use_generator(self, args: CompilerArgs, macro: Macro, macro_args: list[str]) -> CompilerResult:
        pass


class LanguageTarget:
    @abstractmethod
    def transpile(self, compile_lines: list[str], compile_lines_with_labels_comments: list[str],
                  rom_instructions: list[(int, int, int)],
                  rom_instructions_with_labels_comments: list[(int | str, int | None, int | None)],
                  args: CompilerArgs, compiler_working_dir: Path) -> CompilerResult:
        pass


class MacroLoadingState():
    def __init__(self, macro_opener: str, file: str, macro_start_line_no: int):
        self.macro_generator: Type[MacroGenerator] | None = None
        self.generated_macro: bool = False
        self.macro_bottom: list[str] = []
        self.macro_top: list[str] = []
        self.macro_args: list[MacroTypes] = []
        self.macro_end: str | None = None
        self.macro_opener: str = macro_opener
        self.complex_macro: bool = False
        self.currently_macro_top: bool = True
        self.macro_generator_start: int = 0
        self.file: str = file
        self.macro_generator_lang: str = ""
        self.macro_start_line_no = macro_start_line_no


class RegexCache:

    def __init__(self, **key_patern):
        self.key_pattern = key_patern
        self.cache = {}

    def get_by_name(self, name):
        if name not in self.cache:
            self.cache[name] = regex.compile(self.key_pattern[name])
        return self.cache[name]

    def add_pater_name(self, name, pater):
        self.key_pattern[name] = pater

    def add_pattern_if_not_added(self, **args):
        for name, pattern in args.items():
            if name not in self.key_pattern:
                self.key_pattern[name] = pattern
