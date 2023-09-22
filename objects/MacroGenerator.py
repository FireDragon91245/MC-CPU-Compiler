from abc import abstractmethod

from objects.CompilerArgs import CompilerArgs
from objects.CompilerResult import CompilerResult

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects.Macro import Macro


class MacroGenerator:
    @staticmethod
    @abstractmethod
    def get_target_language() -> str:
        pass

    @abstractmethod
    def __init__(self, generator_lines: list[str]) -> None:
        self.generator_lines = generator_lines

    @abstractmethod
    def load_generator(self, args: CompilerArgs, macro: "Macro") -> CompilerResult:
        pass

    @abstractmethod
    def use_generator(self, args: CompilerArgs, macro: "Macro", macro_args: list[str]) -> CompilerResult:
        pass

    def __cmp__(self, other):
        if not isinstance(other, MacroGenerator):
            return False
        return self.generator_lines == other.generator_lines and\
            self.get_target_language() == other.get_target_language()
