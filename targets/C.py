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
            code_lines: list[str] = self.get_code_lines(rom_instructions)
            code_str: str = self.join_ines(code_lines)
            self.replace_all_lines(template_lines, "%code", code_str)
            with open("..\\out.c", "wt") as c_file:
                if not c_file.writable():
                    print(f"[C][ERROR] file out.c is not writable")
                    return
                for line in template_lines:
                    c_file.write(line + "\n")
                c_file.close()

    @staticmethod
    def replace_all_lines(lines: list[str], target: str, replacement: str):
        for line_no, line in enumerate(lines):
            lines[line_no] = line.replace(target, replacement)

    @staticmethod
    def get_code_lines(rom_instructions: list[(int, int, int)]) -> list[str]:
        lines: list[str] = []
        for rom_instruction in rom_instructions:
            inst, arg1, arg2 = rom_instruction
            match inst:
                case 0:  # add %register, %register
                    lines.append(f"registers[{arg1}] = registers[{arg1}] + registers[{arg2}];")
                case 1:  # dynadd %registerpointer, %registerpointer
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]] + registers[registers[{arg2}]];")
                case 2:  # dynadda %registerpointer, %register
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]] + registers[{arg2}];")
                case 3:  # dynaddb %register, %registerpointer
                    lines.append(f"registers[{arg1}] = registers[{arg1}] + registers[registers[{arg2}]];")
                case 4:  # sub %register, %register
                    lines.append(f"registers[{arg1}] = registers[{arg1}] - registers[{arg2}];")
                case 5:  # dynsub %registerpointer, %registerpointer
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]] - registers[registers[{arg2}]];")
                case 6:  # dynsuba %registerpointer, %register
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]] - registers[{arg2}];")
                case 7:  # dynsubb %register, %registerpointer
                    lines.append(f"registers[{arg1}] = registers[{arg1}] - registers[registers[{arg2}]];")
                case 8:  # mult %register, %register
                    lines.append(f"registers[{arg1}] = registers[{arg1}] * registers[{arg2}];")
                case 9:  # dynmult %registerpointer, %registerpointer
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]] * registers[registers[{arg2}]];")
                case 10:  # dynmulta %registerpointer, %register
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]] * registers[{arg2}];")
                case 11:  # dynmultb %register, %registerpointer
                    lines.append(f"registers[{arg1}] = registers[{arg1}] * registers[registers[{arg2}]];")
                case 12:  # div %register, %register
                    lines.append(f"registers[{arg1}] = registers[{arg1}] / registers[{arg2}];")
                case 13:  # dyndiv %registerpointer, %registerpointer
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]] / registers[registers[{arg2}]];")
                case 14:  # dyndiva %registerpointer, %register
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]] / registers[{arg2}];")
                case 15:  # dyndivb %register, %registerpointer
                    lines.append(f"registers[{arg1}] = registers[{arg1}] / registers[registers[{arg2}]];")
                case 16:  # inc %register
                    lines.append(f"registers[{arg1}] = registers[{arg1}]++;")
                case 17:  # dyninc %registerpointer
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]]++;")
                case 18:  # dec %register
                    lines.append(f"registers[{arg1}] = registers[{arg1}]--;")
                case 19:  # dyndec %registerpointer
                    lines.append(f"registers[registers[{arg1}]] = registers[registers[{arg1}]]--;")
                case 20:  # call %number
                    break
            return lines

    @staticmethod
    def join_ines(code_lines: list[str]) -> str:
        code_str: str = ""
        for line in code_lines:
            code_str += line + "\n"
        return code_str


