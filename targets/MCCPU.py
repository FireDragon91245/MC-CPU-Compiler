from compiler_obj import LanguageTarget, CompilerArgs


class MCCPU(LanguageTarget):
    def transpile(self, compile_lines: list[str], rom_instructions: list[(int, int, int)], args: CompilerArgs):
        super().transpile(compile_lines, rom_instructions, None)