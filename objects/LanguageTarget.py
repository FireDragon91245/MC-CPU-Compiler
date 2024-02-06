from abc import abstractmethod
from pathlib import Path

from objects.CompilerArgs import CompilerArgs
from objects.CompilerResult import CompilerResult


class LanguageTarget:
    @abstractmethod
    def transpile(self, compile_lines: list[str], compile_lines_with_labels_comments: list[str],
                  rom_instructions: list[(int, int, int)],
                  rom_instructions_with_labels_comments: list[(int | str, int | None, int | None)],
                  args: CompilerArgs, compiler_working_dir: Path) -> CompilerResult:
        pass
