import os
import pathlib
import re

from compiler_obj import MacroTypes, Macro, CompilerArgs, CompilerResult, CompilerErrorLevels, LanguageTarget

# %number can be equal to %label, only the compiler deals with %label & %variable and is resolved to %number at
# compile time
NATIVE_INSTRUCTIONS: dict[str, int] = {
    "add %register, %register": 1,
    "add %register, %registerpointer": 2,
    "add %register, %number": 3,
    "add %register, %address": 4,
    "add %register, %variable": 4,
    "add %registerpointer, %register": 5,
    "add %registerpointer, %registerpointer": 6,
    "add %registerpointer, %number": 7,
    "add %registerpointer, %address": 8,
    "add %registerpointer, %variable": 8,
    "add %address, %register": 9,
    "add %variable, %register": 9,
    "add %address, %registerpointer": 10,
    "add %variable, %registerpointer": 10,
    "add %address, %number": 11,
    "add %variable, %number": 11,
    "add %address, %address": 12,
    "add %variable, %variable": 12,
    "sub %register, %register": 13,
    "sub %register, %registerpointer": 14,
    "sub %register, %number": 15,
    "sub %register, %variable": 16,
    "sub %register, %address": 16,
    "sub %registerpointer, %register": 17,
    "sub %registerpointer, %registerpointer": 18,
    "sub %registerpointer, %number": 19,
    "sub %registerpointer, %variable": 20,
    "sub %registerpointer, %address": 20,
    "sub %variable, %register": 21,
    "sub %address, %register": 21,
    "sub %variable, %registerpointer": 22,
    "sub %address, %registerpointer": 22,
    "sub %variable, %number": 23,
    "sub %address, %number": 23,
    "sub %variable, %variable": 24,
    "sub %address, %address": 24,
    "mul %register, %register": 25,
    "mul %register, %registerpointer": 26,
    "mul %register, %number": 27,
    "mul %register, %variable": 28,
    "mul %register, %address": 28,
    "mul %registerpointer, %register": 29,
    "mul %registerpointer, %registerpointer": 30,
    "mul %registerpointer, %number": 31,
    "mul %registerpointer, %variable": 32,
    "mul %registerpointer, %address": 32,
    "mul %variable, %register": 33,
    "mul %address, %register": 33,
    "mul %variable, %registerpointer": 34,
    "mul %address, %registerpointer": 34,
    "mul %variable, %number": 35,
    "mul %address, %number": 35,
    "mul %variable, %variable": 36,
    "mul %address, %address": 36,
    "div %register, %register": 37,
    "div %register, %registerpointer": 38,
    "div %register, %number": 39,
    "div %register, %variable": 40,
    "div %register, %address": 40,
    "div %registerpointer, %register": 41,
    "div %registerpointer, %registerpointer": 42,
    "div %registerpointer, %number": 43,
    "div %registerpointer, %variable": 44,
    "div %registerpointer, %address": 44,
    "div %variable, %register": 45,
    "div %address, %register": 45,
    "div %variable, %registerpointer": 46,
    "div %address, %registerpointer": 46,
    "div %variable, %number": 47,
    "div %address, %number": 47,
    "div %variable, %variable": 48,
    "div %address, %address": 48,
    "xor %register, %register": 49,
    "xor %register, %registerpointer": 50,
    "xor %register, %number": 51,
    "xor %register, %variable": 52,
    "xor %register, %address": 52,
    "xor %registerpointer, %register": 53,
    "xor %registerpointer, %registerpointer": 54,
    "xor %registerpointer, %number": 55,
    "xor %registerpointer, %variable": 56,
    "xor %registerpointer, %address": 56,
    "xor %variable, %register": 57,
    "xor %address, %register": 57,
    "xor %variable, %registerpointer": 58,
    "xor %address, %registerpointer": 58,
    "xor %variable, %number": 59,
    "xor %address, %number": 59,
    "xor %variable, %variable": 60,
    "xor %address, %address": 60,
    "and %register, %register": 61,
    "and %register, %registerpointer": 62,
    "and %register, %number": 63,
    "and %register, %variable": 64,
    "and %register, %address": 64,
    "and %registerpointer, %register": 65,
    "and %registerpointer, %registerpointer": 66,
    "and %registerpointer, %number": 67,
    "and %registerpointer, %variable": 68,
    "and %registerpointer, %address": 68,
    "and %variable, %register": 69,
    "and %address, %register": 69,
    "and %variable, %registerpointer": 70,
    "and %address, %registerpointer": 70,
    "and %variable, %number": 71,
    "and %address, %number": 71,
    "and %variable, %variable": 72,
    "and %address, %address": 72,
    "not %register": 73,
    "not %registerpointer": 74,
    "not %variable": 75,
    "not %address": 75,
    "or %register, %register": 76,
    "or %register, %registerpointer": 77,
    "or %register, %number": 78,
    "or %register, %variable": 79,
    "or %register, %address": 79,
    "or %registerpointer, %register": 80,
    "or %registerpointer, %registerpointer": 81,
    "or %registerpointer, %number": 82,
    "or %registerpointer, %variable": 83,
    "or %registerpointer, %address": 83,
    "or %variable, %register": 84,
    "or %address, %register": 84,
    "or %variable, %registerpointer": 85,
    "or %address, %registerpointer": 85,
    "or %variable, %number": 86,
    "or %address, %number": 86,
    "or %variable, %variable": 87,
    "or %address, %address": 87,
    "shr %register, %number": 88,
    "shr %registerpointer, %number": 89,
    "shr %variable, %number": 90,
    "shr %address, %number": 90,
    "shl %register, %number": 91,
    "shl %registerpointer, %number": 92,
    "shl %variable, %number": 93,
    "shl %address, %number": 93,
    "mov %register, %register": 94,
    "mov %register, %registerpointer": 95,
    "mov %register, %number": 96,
    "mov %register, %variable": 97,
    "mov %register, %address": 97,
    "mov %registerpointer, %register": 98,
    "mov %registerpointer, %registerpointer": 99,
    "mov %registerpointer, %number": 100,
    "mov %registerpointer, %variable": 101,
    "mov %registerpointer, %address": 101,
    "mov %variable, %register": 102,
    "mov %address, %register": 102,
    "mov %variable, %registerpointer": 103,
    "mov %address, %registerpointer": 103,
    "mov %variable, %number": 104,
    "mov %address, %number": 104,
    "mov %variable, %variable": 105,
    "mov %address, %address": 105,
    "cmp %register, %register": 106,
    "cmp %register, %registerpointer": 107,
    "cmp %register, %number": 108,
    "cmp %register, %variable": 109,
    "cmp %register, %address": 109,
    "cmp %registerpointer, %register": 110,
    "cmp %registerpointer, %registerpointer": 111,
    "cmp %registerpointer, %number": 112,
    "cmp %registerpointer, %variable": 113,
    "cmp %registerpointer, %address": 113,
    "cmp %variable, %register": 114,
    "cmp %address, %register": 114,
    "cmp %variable, %registerpointer": 115,
    "cmp %address, %registerpointer": 115,
    "cmp %variable, %number": 116,
    "cmp %address, %number": 116,
    "cmp %variable, %variable": 117,
    "cmp %address, %address": 117,
    "jz %number": 118,
    "jz %label": 118,
    "jnz %number": 119,
    "jnz %label": 119,
    "je %number": 120,
    "je %label": 120,
    "jne %number": 121,
    "jne %label": 121,
    "jl %number": 122,
    "jl %label": 122,
    "jle %number": 123,
    "jle %label": 123,
    "jg %number": 124,
    "jg %label": 124,
    "jge %number": 125,
    "jge %label": 125,
    "jmp %number": 126,
    "jmp %label": 126,
    "inc %register": 127,
    "inc %registerpointer": 128,
    "inc %number": 129,
    "inc %variable": 130,
    "inc %address": 130,
    "dec %register": 131,
    "dec %registerpointer": 132,
    "dec %number": 133,
    "dec %variable": 134,
    "dec %address": 134,
    "push %register": 135,
    "push %registerpointer": 136,
    "push %number": 137,
    "push %variable": 138,
    "push %address": 138,
    "pop %register": 139,
    "pop %registerpointer": 140,
    "pop %number": 141,
    "pop %variable": 142,
    "pop %address": 142,
    "call %number": 143,
    "call %label": 143,
    "ret": 144,
    "nop": 145,
    "halt": 146,
}
TYPE_REGEX_MATCH_REPLACERS = {
    "%registerpointer": r"(\[&r[0-9]{1,3}\])",
    "%register": "(&r[0-9]{1,3})",
    "%number": "(0x[0-9A-Fa-f]{1,2}|[0-9]{1,3})",
    "%address": r"(\*0x[0-9A-Fa-f]{1,2}|\*[0-9]{1,3})",
    "%variable": r"(\*[a-zA-Z][a-zA-Z0-9]*)",
    "%label": "(~[a-zA-Z][a-zA-Z0-9_-]*)",
}


def read_lines(file):
    return file.read().splitlines()


def next_memory_address(var_count: int, blocks: int, balance: bool, mem_size: int) -> int:
    if not balance:
        return var_count
    else:
        block = var_count % 8
        cell = (var_count - block) / 8
        address = (mem_size / blocks) * block + cell
        return int(address)


def get_var_memory_address(lines: list[str], variables: dict[str, int], args: CompilerArgs) -> CompilerResult:
    shrt_res: CompilerResult = CompilerResult.empty()
    line_enumerate = enumerate(lines)
    for line_no, line in line_enumerate:
        if line.startswith("#"):
            if line.find("memorylayout") != -1:
                if line.find("explicit") != -1:
                    return shrt_res.not_empty_or_ok()
                elif line.find("auto") != -1 and line.find("static") != -1:
                    if line.find("incremental") != -1:
                        shrt_res.accumulate(find_var_static_auto_all(line_enumerate, variables, False, args))
                        return shrt_res.not_empty_or_ok()
                    elif line.find("balanced") != -1:
                        shrt_res.accumulate(find_var_static_auto_all(line_enumerate, variables, True, args))
                        return shrt_res.not_empty_or_ok()
                    else:
                        find_var_static_auto_all(line_enumerate, variables, False, args)
                        return shrt_res.accumulate(
                            CompilerResult.warn(f"[WARN] No memory balancing type found at #memorylayout ln <{line}>"
                                                f" defaulting to [Incremental]"))
                elif line.find("static") != -1:
                    start_ln = line_no
                    if line.find("incremental") != -1:
                        return shrt_res.accumulate(
                            find_var_static_all(line_enumerate, variables, False, args))
                    elif line.find("balanced") != -1:
                        return shrt_res.accumulate(find_var_static_all(line_enumerate, variables, True, args))
                    else:
                        shrt_res.accumulate(CompilerResult.warn(f"[WARN] No memory balancing type found at "
                                                                f"#memorylayout ln <{start_ln}> defaulting to ["
                                                                f"Incremental]"))
                        return shrt_res.accumulate(
                            find_var_static_all(line_enumerate, variables, False, args))
                else:
                    shrt_res.accumulate(CompilerResult.warn(
                        f"[WARN] #memorylayout at ln<{line_no}> does not contain a valid variable layout type token ["
                        f"static / static auto / explicit] + address balancing type [incremental / balanced] "
                        f"continuing search for other #memorylayout sections"))
    return shrt_res.accumulate(CompilerResult.warn(
        "[WARN] No #memorylayout section found or no valid variable layout type token found [static / static auto / "
        "explicit] + address balancing type [incremental / balanced] defaulting to [static auto incremental]"))


def find_var_static_all(line_enumerate: enumerate[str], variables: dict[str, int], balanced: bool,
                        args: CompilerArgs) -> CompilerResult:
    var_count = 0
    while True:
        line_no, line = next(line_enumerate, (None, None))
        if line is None:
            return CompilerResult.error("[ERROR] Expected #endmemorylayout after #ememorylayout at ln <{start_ln}>")
        if line.find("#endmemorylayout") != -1:
            return CompilerResult.ok()
        variables[line] = next_memory_address(var_count, args.memory_blocks, balanced, args.mem_size)
        var_count = var_count + 1


def find_var_static_auto_all(line_enumerate: enumerate[str], variables: dict[str, int], balanced: bool,
                             args: CompilerArgs) -> CompilerResult:
    re_var = r"\*([a-zA-Z][a-zA-Z0-9]*)"
    re_var_comp = re.compile(re_var)
    var_count = 0
    while True:
        line_no, line = next(line_enumerate, (None, None))
        if line is None:
            return CompilerResult.ok()
        matches = re_var_comp.findall(line)
        for match in matches:
            if variables.get(match) is None:
                variables[match] = next_memory_address(var_count, args.memory_blocks, balanced, args.mem_size)
                var_count = var_count + 1


def get_imported_files(imported_files, lines, file) -> CompilerResult:
    include_match = r"<([a-z|0-9|A-Z|.|_|-]+)>"
    for line_no, line in enumerate(lines):
        if line.startswith('#'):
            if line.find("includemacrofile") != -1:
                matches: list[str] = re.findall(include_match, line)
                for match in matches:
                    curr_dir = os.getcwd()
                    if os.path.isfile(curr_dir + "/macrodefs/" + match + ".mccpu"):
                        file = open(curr_dir + "/macrodefs/" + match + ".mccpu", "rt")
                        if not file.readable():
                            return CompilerResult.error(
                                f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value "
                                f"\"{line}\" was not found, exiting!")
                        if imported_files.get(match) is not None:
                            continue
                        imported_files[match] = read_lines(file)
                        get_imported_files(imported_files, imported_files.get(match),
                                           curr_dir + "/macrodefs/" + match + ".mccpu")
                    elif os.path.isfile(curr_dir + "/" + match):
                        file = open(curr_dir + "/" + match, "rt")
                        if not file.readable():
                            return CompilerResult.error(
                                f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value "
                                f"\"{line}\" was not found exiting!")
                        if imported_files.get(match) is not None:
                            continue
                        imported_files[match] = read_lines(file)
                        get_imported_files(imported_files, imported_files.get(match), curr_dir + match)
                    else:
                        return CompilerResult.error(
                            f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value "
                            f"\"{line}\" was not found exiting!")
    return CompilerResult.ok()


def get_macro_arg_types(macro_opener, file, line_no) -> list[MacroTypes] | CompilerResult:
    type_reg = r"%[a-zA-Z]*"
    matches: list[str] = re.findall(type_reg, macro_opener)
    macro_types: list[MacroTypes] = []
    for match in matches:
        if match == "%label":
            macro_types.append(MacroTypes.LABEL)
        elif match == "%variable":
            macro_types.append(MacroTypes.VARIABLE)
        elif match == "%address":
            macro_types.append(MacroTypes.MEMORY_ADDRESS)
        elif match == "%number":
            macro_types.append(MacroTypes.NUMBER)
        elif match == "%register":
            macro_types.append(MacroTypes.REGISTER)
        elif match == "%registerpointer":
            macro_types.append(MacroTypes.REGISTER_POINTER)
        else:
            return CompilerResult.error(
                f"[ERROR] macro \"{macro_opener}\" in file \"{file}\" at line <{line_no}> used not valid type "
                f"\"{match}\" valid are [%label, %variable, %address, %number, %register, %registerpointer]")
    return macro_types


def load_macros(macros: dict[int, Macro], file, lines: list[str]) -> CompilerResult:
    macro_reg = r"#\s*macro\s*(.+)"
    macro_end_reg = r"#\s*endmacro\s*(.+)?"
    macro_reg_com = re.compile(macro_reg)
    macro_end_reg_com = re.compile(macro_end_reg)
    lines_iter = enumerate(lines)
    for line_no, line in lines_iter:
        matches = macro_reg_com.match(line)
        if matches is None:
            continue
        if len(matches.groups()) >= 1:
            macro_opener = matches.group(1)
            macro_args = get_macro_arg_types(macro_opener, file, line_no)
            if isinstance(macro_args, CompilerResult):
                return macro_args
            macro_top: list[str] = []
            macro_bottom: list[str] = []
            complex_macro = False
            currently_macro_top = True
            macro_start_line_no = line_no
            while True:
                line_no, line = next(lines_iter, (None, None))
                if line is None:
                    return CompilerResult.error(
                        f"[ERROR] Expected #endmacro after #macro in file \"{file}\" at line <{macro_start_line_no}>")
                if line.startswith("//"):
                    continue
                macro_end_matches = macro_end_reg_com.match(line)
                if line == "...":
                    complex_macro = True
                    currently_macro_top = False
                elif macro_end_matches is not None:
                    if complex_macro:
                        if not (len(macro_end_matches.groups()) >= 1):
                            return CompilerResult.error(f"[ERROR] Complex macros (macros using \"...\") need to have "
                                                        f"a closing expression error at #endmacro in file \"{file}\" "
                                                        f"at line <{line_no}>")
                        macros[abs(hash(macro_opener))] = Macro(macro_opener, macro_end_matches.group(1), macro_args,
                                                                macro_top,
                                                                macro_bottom, complex_macro)
                    else:
                        if len(macro_end_matches.groups()) == 1:
                            macros[abs(hash(macro_opener))] = Macro(macro_opener, "", macro_args, macro_top,
                                                                    macro_bottom, complex_macro)
                        else:
                            macros[abs(hash(macro_opener))] = Macro(macro_opener, macro_end_matches.group(1),
                                                                    macro_args, macro_top,
                                                                    macro_bottom, complex_macro)
                    break
                else:
                    if line.startswith("#comment"):
                        line = line.replace("#comment", "//")
                    if currently_macro_top:
                        macro_top.append(line)
                    else:
                        macro_bottom.append(line)
    return CompilerResult.ok()


def match_instruction(inst: str, line: str) -> bool:
    inst = escape_instruction(inst)
    for t, repl in TYPE_REGEX_MATCH_REPLACERS.items():
        inst = inst.replace(t, repl)

    res = re.match(inst, line)
    return bool(res)


def is_only_native_instructions(curr_compile_lines: list[str]):
    for line in curr_compile_lines:
        if line == '':
            continue
        if line.startswith('#'):
            continue
        if line.startswith("//"):
            continue
        if re.match(r"[a-zA-Z][a-zA-Z0-9_-]+:", line) is not None:
            continue
        found = False
        for inst in NATIVE_INSTRUCTIONS.keys():
            if match_instruction(inst.lower(), line):
                found = True
                break
        if not found:
            return False
    return True


def resolve_args(macro_line, args, macro: Macro, macro_id: int):
    for i in range(0, len(args.groups())):
        macro_line = macro_line.replace(f"%{i + 1}", args.group(i + 1)).replace("%__macro_id", str(macro_id)). \
            replace("%__macro_no", str(macro.macro_no)).replace("%__macro_head", macro.macro_opener)
    return macro_line


def escape_instruction(inst: str) -> str:
    return inst.replace("(", r"\(").replace("{", r"\{").replace(")", r"\)").replace("}", r"\}")


def resolve_macro(curr_compile_lines: list[str], line_no: int, macro: Macro, macro_id: int, macros: list[Macro]) -> int:
    macro.macro_no = macro.macro_no + 1
    macro_pattern = escape_instruction(macro.macro_opener)
    for t, repl in TYPE_REGEX_MATCH_REPLACERS.items():
        macro_pattern = macro_pattern.replace(t, repl)
    args = re.match(macro_pattern, curr_compile_lines[line_no])

    if macro.complex_macro:
        level = 0
        macro_line_no = line_no
        body: list[str] = []
        while macro_line_no < len(curr_compile_lines) - 1:
            macro_line_no = macro_line_no + 1
            for curr_macro in macros:
                if curr_macro.macro_closer == macro.macro_closer:
                    if match_instruction(macro.macro_opener, curr_compile_lines[macro_line_no]):
                        level = level + 1
            if curr_compile_lines[macro_line_no] == macro.macro_closer:
                if level > 0:
                    level = level - 1
                else:
                    break
            body.append(curr_compile_lines[macro_line_no])
        del curr_compile_lines[line_no:macro_line_no + 1]
        for i in reversed(range(0, len(macro.macro_bottom))):
            curr_compile_lines.insert(line_no, resolve_args(macro.macro_bottom[i], args, macro, macro_id))
        for i in reversed(range(0, len(body))):
            curr_compile_lines.insert(line_no, resolve_args(body[i], args, macro, macro_id))
        for i in reversed(range(0, len(macro.macro_top))):
            curr_compile_lines.insert(line_no, resolve_args(macro.macro_top[i], args, macro, macro_id))
        return line_no + len(macro.macro_top) + len(body) + len(macro.macro_bottom)
    else:
        del curr_compile_lines[line_no]
        for i in reversed(range(0, len(macro.macro_top))):
            curr_compile_lines.insert(line_no, resolve_args(macro.macro_top[i], args, macro, macro_id))
        return line_no + len(macro.macro_top)


def resolve_macros(curr_compile_lines: list[str], macros: dict[int, Macro]) -> CompilerResult:
    for line_no in range(len(curr_compile_lines)):
        found = False
        if curr_compile_lines[line_no] == '':
            continue
        for macro_id, macro in macros.items():
            if match_instruction(macro.macro_opener, curr_compile_lines[line_no]):
                line_no = resolve_macro(curr_compile_lines, line_no, macro, macro_id, list(macros.values()))
                if line_no == -1:
                    assert False  # Unknwo error or cause for line_no investigate if trigered
                found = True
                break
        if found:
            continue
        for inst in NATIVE_INSTRUCTIONS.keys():
            if match_instruction(inst.lower(), curr_compile_lines[line_no]):
                found = True
                break
        if found:
            continue
        if re.match(r"[a-zA-Z][a-zA-Z0-9_-]+:", curr_compile_lines[line_no]) is not None:  # excluded label declarations
            continue
        if curr_compile_lines[line_no].startswith("//"):
            continue
        if not found:
            return CompilerResult.error(
                f"[ERROR] can not resolve instruction \"{curr_compile_lines[line_no]}\" "
                f"to any macro or std instruction")
    return CompilerResult.ok()


def write_file(file_name, curr_compile_lines):
    file = open(file_name, "wt")
    for line in curr_compile_lines:
        file.write(line + "\n")
    file.close()


def copy_lines_exclude_compiler_instructions(curr_compile_lines: list[str], lines: list[str]) -> CompilerResult:
    ln_enum = enumerate(lines)
    for ln_no, ln in ln_enum:
        if ln.startswith("#memorylayout"):
            line_no_start = ln_no
            while ln.find("#endmemorylayout") == -1:
                ln_no, ln = next(ln_enum, (None, None))
                if ln is None:
                    return CompilerResult.error(
                        f"[ERROR] expected #endmemorylayout after #memorylayout at ln <{line_no_start}>")
        elif ln.startswith("#macro"):
            line_no_start = ln_no
            while not ln.startswith("#endmacro"):
                ln_no, ln = next(ln_enum, (None, None))
                if ln is None:
                    return CompilerResult.error(f"[ERROR] expected #endmacro after #macro at ln <{line_no_start}>")
        elif ln.startswith("#"):
            continue
        else:
            curr_compile_lines.append(ln)
    return CompilerResult.ok()


def resolve_labels(curr_compile_lines: list[str]) -> bool:
    curr = 0
    max_iter = 1000
    finished = False
    label_re = r"([a-zA-Z][a-zA-Z0-9_-]+):"
    label_re_comp = re.compile(label_re)

    while curr < max_iter and not finished:
        curr = curr + 1
        found = False
        instruction_no = 0
        for line_no in range(len(curr_compile_lines)):
            if curr_compile_lines[line_no].startswith('//') or curr_compile_lines[line_no] == '':
                continue
            instruction_no = instruction_no + 1
            matches = label_re_comp.match(curr_compile_lines[line_no])
            if matches is not None:
                if len(matches.groups()) > 0:
                    found = True
                    del curr_compile_lines[line_no]
                    for i in range(len(curr_compile_lines)):
                        curr_compile_lines[i] = curr_compile_lines[i].replace("~" + matches.group(1),
                                                                              f"{instruction_no}")
                    break
        if not found:
            break
    if not curr < max_iter:
        print(f"[ERROR] Internal compiler error to many labels max of {max_iter} reached")
        return False
    return True


def resolve_variables(curr_compile_lines: list[str], variable_memory_pos: dict[str, int]):
    for line_no in range(len(curr_compile_lines)):
        for var, address in variable_memory_pos.items():
            curr_compile_lines[line_no] = curr_compile_lines[line_no].replace(f"*{var}", f"*{address:.0f}")


def instructions_to_rom(curr_compile_lines: list[str], rom_translation: list[(int, int, int)]) -> CompilerResult:
    for line in curr_compile_lines:
        if line == '':
            continue
        if line.startswith('//'):
            continue
        for inst, inst_id in NATIVE_INSTRUCTIONS.items():
            if match_instruction(inst, line):
                parts = line.split(' ')
                if not add_rom_instruction(inst_id, parts, rom_translation):
                    return CompilerResult.error(
                        f"[ERROR] instruction \"{line}\" contains parts that can not be converted to rom instructions"
                        f" (Probably compiler problem)")
                break
        else:
            return CompilerResult.error(
                f"[ERROR] Instruction \"{line}\" can not be resolved to a Native instruction after compiling,"
                f" exiting! (Probably compiler problem)")
    return CompilerResult.ok()


def call_language_handler(curr_compile_lines: list[str], curr_compile_lines_label: list[str],
                          rom_instructions: list[(int, int, int)],
                          rom_instructions_label: list[(int | str, int | None, int | None)],
                          args: CompilerArgs) -> CompilerResult:
    module = __import__(f"targets.{args.target_lang.upper()}")
    if module is None:
        return CompilerResult.error(f"[ERROR] Canot find language modul for language \"{args.target_lang}\"")
    lang_module = getattr(module, args.target_lang.upper(), None)
    if lang_module is None:
        return CompilerResult.error(f"[ERROR] Language modul \"{args.target_lang}\" did not contain a handler class")
    lang_class = getattr(lang_module, args.target_lang.upper(), None)
    if lang_class is None:
        return CompilerResult.error(f"[ERROR] Language modul \"{args.target_lang}\" did not contain a handler class")
    lang_func = getattr(lang_class, f"{LanguageTarget.transpile.__name__}", None)
    if lang_func is None:
        return CompilerResult.error(f"[ERROR] Language class \"{args.target_lang}\" did not contain a handler function")
    try:
        res = lang_func(lang_class, curr_compile_lines, curr_compile_lines_label, rom_instructions,
                        rom_instructions_label, args, pathlib.Path(os.getcwd()))
        if not isinstance(res, CompilerResult):
            raise TypeError(
                f"{args.target_lang.upper()}.{LanguageTarget.transpile.__name__}() return type expected "
                f"{CompilerResult.__module__}.{CompilerResult.__name__} got"
                f" {type(res).__module__}.{type(res).__name__}")
        return res
    except TypeError as e:
        return CompilerResult.error(
            f"[ERROR] Handler function for {args.target_lang} has the wrong argument types, count or return Type,"
            f" Details: {e.__str__()}")


def instructions_to_rom_labels(curr_compile_lines_labels: list[str],
                               rom_instructions_labels: list[
                                   (int | str, int | None | str, int | None)]) -> CompilerResult:
    for line in curr_compile_lines_labels:
        m = re.match(r"[a-zA-Z][a-zA-Z0-9_-]+:", line)
        if line == '':
            continue
        if line.startswith('//'):
            rom_instructions_labels.append((line, None, None))
            continue
        if m is not None:
            rom_instructions_labels.append((m, None, None))
            continue
        for inst, inst_id in NATIVE_INSTRUCTIONS.items():
            if match_instruction(inst, line):
                parts = line.replace('*', '').split(' ')
                if inst.find("%label"):
                    if len(parts) > 2:
                        rom_instructions_labels.append((inst_id, parts[1], parts[2]))
                    elif len(parts) > 1:
                        rom_instructions_labels.append((inst_id, parts[1], 0))
                    else:
                        rom_instructions_labels.append((inst_id, 0, 0))
                else:
                    if not add_rom_instruction(inst_id, parts, rom_instructions_labels):
                        return CompilerResult.error(
                            f"[ERROR] instruction \"{line}\" contains parts that can not be converted to rom"
                            f" instructions (Probably compiler problem)")
                break
        else:
            return CompilerResult.error(
                f"[ERROR] Instruction \"{line}\" can not be resolved to a Native instruction after compiling,"
                " exiting!")
    return CompilerResult.ok()


def num_to_int(param: str) -> int:
    return int(param, 0)


def register_to_int(param: str) -> int:
    return int(re.findall(r"&r([0-9]{1,3})|$", param)[0])


def inst_arg_to_rom(param: str) -> int | str:
    if (match := re.match(TYPE_REGEX_MATCH_REPLACERS["%number"], param)) is not None:
        return num_to_int(match.group(1))
    elif (match := re.match(TYPE_REGEX_MATCH_REPLACERS["%register"], param)) is not None:
        return register_to_int(match.group(1))
    elif (match := re.match(TYPE_REGEX_MATCH_REPLACERS["%address"], param)) is not None:
        return num_to_int(match.group(1).replace("*", ""))
    elif (match := re.match(TYPE_REGEX_MATCH_REPLACERS["%registerpointer"], param)) is not None:
        return register_to_int(match.group(1))
    elif (match := re.match(TYPE_REGEX_MATCH_REPLACERS["%label"], param)) is not None:
        return match.group(1)
    else:
        return -1


def add_rom_instruction(inst_id, parts, rom_instructions_labels) -> bool:
    if len(parts) > 2:
        part_1 = inst_arg_to_rom(parts[1])
        if part_1 == -1:
            return False
        part_2 = inst_arg_to_rom(parts[2])
        if part_2 == -1:
            return False
        rom_instructions_labels.append((inst_id, part_1, part_2))
    elif len(parts) > 1:
        part_1 = inst_arg_to_rom(parts[1])
        if part_1 == -1:
            return False
        rom_instructions_labels.append((inst_id, part_1, 0))
    else:
        rom_instructions_labels.append((inst_id, 0, 0))
    return True


def handle_error(res: CompilerResult, args: CompilerArgs) -> CompilerResult | None:
    if res.status.is_severity_higher(CompilerErrorLevels.OK):
        if res.message_count() == 1:
            print(f"{res.status} {res.message}")
        else:
            for msg in res.messages:
                print(f"{msg[0]} {msg[1]}")
    match res.status:
        case CompilerErrorLevels.ERROR:
            return None if args.exit_level == CompilerErrorLevels.NONE else res
        case CompilerErrorLevels.WARNING:
            return None if args.exit_level == CompilerErrorLevels.ERROR \
                           or args.exit_level == CompilerErrorLevels.NONE else res
        case CompilerErrorLevels.OK:
            return None


def compile_file(file_path: str, args: CompilerArgs) -> CompilerResult:
    result: CompilerResult = CompilerResult.empty()

    file = open(file_path, "rt")

    if not file.readable():
        if handle_error(result.accumulate(CompilerResult.error("Input File Not Readable")), args) is not None:
            return result

    lines = read_lines(file)

    file.close()

    for ind, val in enumerate(lines):
        lines[ind] = val.lower().strip()

    imported_files: dict[str, list[str]] = {}

    if handle_error(result.accumulate(get_imported_files(imported_files, lines, file_path)), args) is not None:
        return result

    for file, file_lines in imported_files.items():
        for file_line_no in range(len(file_lines)):
            file_lines[file_line_no] = file_lines[file_line_no].lower().strip()

    macros: dict[int, Macro] = {}
    for file, included_lines in imported_files.items():
        if handle_error(result.accumulate(load_macros(macros, file, included_lines)), args) is not None:
            return result

    if handle_error(result.accumulate(load_macros(macros, file_path, lines)), args) is not None:
        return result

    variable_memory_pos: dict[str, int] = {}
    if handle_error(result.accumulate(get_var_memory_address(lines, variable_memory_pos, args)), args) is not None:
        return result

    curr_compile_lines: list[str] = []

    if handle_error(result.accumulate(copy_lines_exclude_compiler_instructions(curr_compile_lines, lines)),
                    args) is not None:
        return result

    depth_limit = 1_000
    curr_depth = 0
    while not is_only_native_instructions(curr_compile_lines):
        curr_depth = curr_depth + 1
        if handle_error(result.accumulate(resolve_macros(curr_compile_lines, macros)), args) is not None:
            return result
        if curr_depth >= depth_limit:
            if handle_error(result.accumulate(CompilerResult.error(
                    "[ERROR] recursive macro? encountered depth of {depth_limit} and still found unresolved macros.")),
                    args) is None:
                return result

    handle_error(result.accumulate(CompilerResult.info("[INFO] Macros resolved")), args)

    resolve_variables(curr_compile_lines, variable_memory_pos)
    handle_error(result.accumulate(CompilerResult.info("[INFO] Variables resolved")), args)

    curr_compile_lines_labels: list[str] = curr_compile_lines.copy()

    resolve_labels(curr_compile_lines)
    handle_error(result.accumulate(CompilerResult.info("[INFO] Labels resolved")), args)

    rom_instructions: list[(int, int, int)] = []
    rom_instructions_labels: list[(int | str, int | None, int | None)] = []

    if handle_error(result.accumulate(instructions_to_rom(curr_compile_lines, rom_instructions)), args) is not None:
        return result
    if handle_error(result.accumulate(instructions_to_rom_labels(curr_compile_lines_labels, rom_instructions_labels)),
                    args) is not None:
        return result

    if handle_error(result.accumulate(
            call_language_handler(curr_compile_lines, curr_compile_lines_labels, rom_instructions,
                                  rom_instructions_labels,
                                  args)), args) is not None:
        return result

    return result.not_empty_or_ok()
