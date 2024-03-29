from pathlib import Path

from objects.LanguageTarget import LanguageTarget
from objects.CompilerResult import CompilerResult
from objects.CompilerArgs import CompilerArgs


class MCCPU(LanguageTarget):

    def transpile(self, compile_lines: list[str], compile_lines_with_labels_comments: list[str],
                  rom_instructions: list[(int, int, int)],
                  rom_instructions_with_labels_comments: list[(int | str, int | None, int | None)], args: CompilerArgs,
                  compiler_working_dir: Path) -> CompilerResult:
        return CompilerResult.ok()

    @staticmethod
    def get_code(rom_instructions_with_labels_comments) -> list[str]:
        code: list[str] = []
        for inst in rom_instructions_with_labels_comments:
            inst, arg1, arg2 = inst
            match inst:
                case _:
                    print("Not Implemented")
                # TODO: instruction translation
        return code

    @staticmethod
    def translate_register(register: int) -> str:
        match register:
            case 0:
                return "rax"
            case 1:
                return "rbx"
            case 2:
                return "rcx"
            case 3:
                return "rdx"
            case 4:
                return "rsi"
            case 5:
                return "rdi"
            case 6:
                return "rbp"
            case 7:
                return "rsp"
            case 8:
                return "r8"
            case 9:
                return "r9"
            case 10:
                return "r10"
            case 11:
                return "r11"
            case 12:
                return "r12"
            case 13:
                return "r13"
            case 14:
                return "r14"
            case 15:
                return "r15"
            case _:
                print(f"[ASM][ERROR] Invalid register: {register} for x86-64")
