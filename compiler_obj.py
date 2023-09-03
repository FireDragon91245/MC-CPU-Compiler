from enum import Enum
from pathlib import Path


class MacroTypes(Enum):
    LABEL = 1
    VARIABLE = 2
    MEMORY_ADDRESS = 3
    NUMBER = 4
    REGISTER = 5
    REGISTER_POINTER = 6


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
                 macro_bottom: list[str], complex_macro: bool) -> None:
        self.complex_macro = complex_macro
        self.macro_bottom = macro_bottom
        self.macro_top = macro_top
        self.macro_args = macro_args
        self.macro_closer = macro_closer
        self.macro_opener = macro_opener
        self.macro_no = 0

    def __cmp__(self, other):
        return self.complex_macro == other.complex_macro and self.macro_bottom == other.macro_bottom and self.macro_top == other.macro_top and self.macro_args == other.macro_args and self.macro_closer == other.macro_closer and self.macro_opener == other.macro_opener


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


class LanguageTarget:

    def transpile(self, compile_lines: list[str], compile_lines_with_labels_comments: list[str],
                  rom_instructions: list[(int, int, int)],
                  rom_instructions_with_labels_comments: list[(int | str, int | None, int | None)],
                  args: CompilerArgs, compiler_root_dir: Path) -> CompilerResult:
        pass
