from compiler_obj import LanguageTarget, CompilerArgs


class C(LanguageTarget):

    def transpile(self, compile_lines: list[str], rom_instructions: list[(int, int, int)], args: CompilerArgs):
        with open("C.c", "rt") as c_template_file:
            if not c_template_file.readable():
                print(f"[C][ERROR] file C.c is not readable")
                return
            template_lines = c_template_file.read().splitlines()
            self.replace_all_lines(template_lines, "%memory_size", f"{args.mem_size:.0f}")
            self.replace_all_lines(template_lines, "%stack_size", f"{args.stack_size:.0f}")
            self.replace_all_lines(template_lines, "%register_count", f"{args.register_count:.0f}")


    def replace_all_lines(self, lines: list[str], target: str, replacement: str):
        for line_no, line in enumerate(lines):
            lines[line_no] = line.replace(target, replacement)