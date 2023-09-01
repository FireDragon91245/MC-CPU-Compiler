from enum import Enum


class MacroTypes(Enum):
    LABEL = 1
    VARIABLE = 2
    MEMORY_ADDRESS = 3
    NUMBER = 4
    REGISTER = 5
    REGISTER_POINTER = 6


class CompilerResultStatus(Enum):
    OK = 1
    WARNING = 2
    ERROR = 3

    def is_severity_higher(self, other):
        return self.value > other.value


class CompilerErrorLevel(Enum):
    ERROR = 1
    WARNING = 2
    INFO = 3
    NONE = 4


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
                 register_count: int, exit_level: CompilerErrorLevel) -> None:
        self.exit_level = exit_level
        self.register_count = register_count
        self.memory_blocks = memory_blocks
        self.mem_size = mem_size
        self.target_lang = target_lang
        self.stack_size = stack_size


class LanguageTarget:

    def transpile(self, compile_lines: list[str], compile_lines_with_labels_comments: list[str], rom_instructions: list[(int, int, int)], rom_instructions_with_labels_comments: list[(int | str, int | None, int | None)], args: CompilerArgs):
        pass


class CompilerResult:

    def __init__(self, status: CompilerResultStatus | None, message: str | None) -> None:
        self.message = message
        self.status = status
        self.messages: list[(CompilerResultStatus, str)] = []

    @staticmethod
    def ok():
        return CompilerResult(CompilerResultStatus.OK, "")

    @staticmethod
    def error(message: str):
        return CompilerResult(CompilerResultStatus.ERROR, message)

    @staticmethod
    def warn(message: str):
        return CompilerResult(CompilerResultStatus.WARNING, message)

    def acumulate(self, other):
        if self.message is None and self.status is None:
            self.status = other.status
            self.message = other.message
            return

        if len(self.messages) == 0:
            self.messages.append((self.status, self.message))

        if other.status.is_severity_higher(self.status):
            self.status = other.status

        self.messages.append((other.status, other.message))

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


    def empty(self):
        return CompilerResult(None, None)
