from compiler_obj import LanguageTarget, CompilerArgs


class MCCPU(LanguageTarget):

    def transpile(self, compile_lines: list[str], compile_lines_with_labels_comments: list[str],
                  rom_instructions: list[(int, int, int)],
                  rom_instructions_with_labels_comments: list[(int | str, int | None, int | None)], args: CompilerArgs):
        with open("..\\out.mccpu", "w") as f:
            f.write("\n".join(compile_lines))