import os
import re

from compiler_obj import MacroTypes, Macro, CompilerArgs

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


def get_var_memory_address(lines: list[str], variables: dict[str, int], args: CompilerArgs):
    line_enumerate = enumerate(lines)
    for line_no, line in line_enumerate:
        if line.startswith("#"):
            if line.find("memorylayout") != -1:
                if line.find("explicit") != -1:
                    return True
                elif line.find("auto") != -1 and line.find("static") != -1:
                    if line.find("incremental") != -1:
                        find_var_static_auto_all(line_enumerate, variables, False, args)
                        return True
                    elif line.find("balanced") != -1:
                        find_var_static_auto_all(line_enumerate, variables, True, args)
                        return True
                    else:
                        print(f"[WARN] No memory balancing type found at #memorylayout ln <{line}> defaulting to "
                              f"[Incremental]")
                        find_var_static_auto_all(line_enumerate, variables, False, args)
                        return True
                elif line.find("static") != -1:
                    start_ln = line_no
                    if line.find("incremental") != -1:
                        return find_var_static_all(line_enumerate, start_ln, variables, False, args)
                    elif line.find("balanced") != -1:
                        return find_var_static_all(line_enumerate, start_ln, variables, True, args)
                    else:
                        print(f"[WARN] No memory balancing type found at #memorylayout ln <{start_ln}> defaulting to "
                              f"[Incremental]")
                        return find_var_static_all(line_enumerate, start_ln, variables, False, args)
                else:
                    print(
                        f"[WARN] #memorylayout at ln<{line_no}> does not contain a valid variable layout type token ["
                        f"static / static auto / explicit] + address balancing type [incremental / balanced] "
                        f"continuing search for other #memorylayout sections")
    print(
        "[WARN] No #memorylayout section found or no valid variable layout type token found [static / static auto / "
        "explicit] + address balancing type [incremental / balanced] defaulting to [static auto incremental]")
    return True


def find_var_static_all(line_enumerate: enumerate[str], start_ln: int, variables: dict[str, int], balanced: bool,
                        args: CompilerArgs):
    var_count = 0
    while True:
        line_no, line = next(line_enumerate, (None, None))
        if line is None:
            print(f"[ERROR] Expected #endmemorylayout after #ememorylayout at ln <{start_ln}>")
            return False
        if line.find("#endmemorylayout") != -1:
            return True
        variables[line] = next_memory_address(var_count, args.memory_blocks, balanced, args.mem_size)
        var_count = var_count + 1


def find_var_static_auto_all(line_enumerate: enumerate[str], variables: dict[str, int], balanced: bool,
                             args: CompilerArgs) -> None:
    re_var = r"\*([a-zA-Z][a-zA-Z0-9]*)"
    re_var_comp = re.compile(re_var)
    var_count = 0
    while True:
        line_no, line = next(line_enumerate, (None, None))
        if line is None:
            return
        matches = re_var_comp.findall(line)
        for match in matches:
            if variables.get(match) is None:
                variables[match] = next_memory_address(var_count, args.memory_blocks, balanced, args.mem_size)
                var_count = var_count + 1


def get_imported_files(imported_files, lines, file):
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
                            print(
                                f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value "
                                f"\"{line}\" was not found, exiting!")
                            return False
                        if imported_files.get(match) is not None:
                            continue
                        imported_files[match] = read_lines(file)
                        get_imported_files(imported_files, imported_files.get(match),
                                           curr_dir + "/macrodefs/" + match + ".mccpu")
                    elif os.path.isfile(curr_dir + "/" + match):
                        file = open(curr_dir + "/" + match, "rt")
                        if not file.readable():
                            print(
                                f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value "
                                f"\"{line}\" was not found exiting!")
                            return False
                        if imported_files.get(match) is not None:
                            continue
                        imported_files[match] = read_lines(file)
                        get_imported_files(imported_files, imported_files.get(match), curr_dir + match)
                    else:
                        print(
                            f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value "
                            f"\"{line}\" was not found exiting!")
                        return False
    return True


def get_macro_arg_types(macro_opener, file, line_no) -> list[MacroTypes] | None:
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
        else:
            print(
                f"[ERROR] macro \"{macro_opener}\" in file \"{file}\" at line <{line_no}> used not valid type "
                f"\"{match}\" valid are [%label, %variable, %address, %number, %register]")
            return None
    return macro_types


def load_macros(macros, file, lines: list[str]):
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
            if macro_args is None:
                return False
            macro_top: list[str] = []
            macro_bottom: list[str] = []
            complex_macro = False
            currently_macro_top = True
            macro_start_line_no = line_no
            while True:
                line_no, line = next(lines_iter, (None, None))
                if line is None:
                    print(f"[ERROR] Expected #endmacro after #macro in file \"{file}\" at line <{macro_start_line_no}>")
                    return False
                if line.startswith("//"):
                    continue
                macro_end_matches = macro_end_reg_com.match(line)
                if line == "...":
                    complex_macro = True
                    currently_macro_top = False
                elif macro_end_matches is not None:
                    if complex_macro:
                        if not (len(macro_end_matches.groups()) >= 1):
                            print(f"[ERROR] Complex macros (macros using \"...\") need to have a closing expression "
                                  f"error at #endmacro in file \"{file}\" at line <{line_no}>")
                            return False
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
    return True


def match_instruction(inst, line) -> bool | None:
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


def resolve_macros(curr_compile_lines: list[str], macros: dict[int, Macro]) -> bool:
    for line_no in range(len(curr_compile_lines)):
        found = False
        if curr_compile_lines[line_no] == '':
            continue
        for macro_id, macro in macros.items():
            if match_instruction(macro.macro_opener, curr_compile_lines[line_no]):
                line_no = resolve_macro(curr_compile_lines, line_no, macro, macro_id, list(macros.values()))
                if line_no == -1:
                    return False
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
            print(
                f"[ERROR] can not resolve instruction \"{curr_compile_lines[line_no]}\" "
                f"to any macro or std instruction")
            return False
    return True


def write_file(file_name, curr_compile_lines):
    file = open(file_name, "wt")
    for line in curr_compile_lines:
        file.write(line + "\n")
    file.close()


def copy_lines_exclude_compiler_instructions(curr_compile_lines: list[str], lines: list[str]) -> bool:
    for line_no in range(len(lines)):
        if lines[line_no].startswith("#memorylayout"):
            line_no_start = line_no
            while lines[line_no].find("#endmemorylayout") == -1:
                line_no = line_no + 1
                if line_no >= len(lines):
                    print(f"[ERROR] expected #endmemorylayout after #memorylayout at ln <{line_no_start}>")
                    return False
        elif lines[line_no].startswith("#macro"):
            line_no_start = line_no
            while not lines[line_no].startswith("#endmacro"):
                line_no = line_no + 1
                if line_no >= len(lines):
                    print(f"[ERROR] expected #endmacro after #macro at ln <{line_no_start}>")
                    return False
        elif lines[line_no].startswith("#"):
            continue
        else:
            curr_compile_lines.append(lines[line_no])


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


def instructions_to_rom(curr_compile_lines: list[str], rom_translation: list[(int, int, int)]) -> bool:
    for line in curr_compile_lines:
        if line == '':
            continue
        if line.startswith('//'):
            continue
        for inst, inst_id in NATIVE_INSTRUCTIONS.items():
            if match_instruction(inst, line):
                parts = line.replace('*', '').split(' ')
                add_rom_instruction(inst_id, parts, rom_translation)
            else:
                print(f"[ERROR] Instruction \"{line}\" can not be resolved to a Native instruction after compiling,"
                      " exiting!")
                return False
    return True


def call_language_handler(curr_compile_lines: list[str], curr_compile_lines_label: list[str], rom_instructions: list[(int, int, int)], rom_instructions_label: list[(int | str, int | None, int | None)], args: CompilerArgs):
    module = __import__(f"targets.{args.target_lang.upper()}")
    if module is None:
        print(f"[ERROR] Canot find language modul for language \"{args.target_lang}\"")
        return
    lang_class = getattr(module, args.target_lang.upper(), None)
    if lang_class is None:
        print(f"[ERROR] Language modul \"{args.target_lang}\" did not contain a handler class")
        return
    lang_func = getattr(lang_class, "transpile", None)
    if lang_func is None:
        print(f"[ERROR] Language class \"{args.target_lang}\" did not contain a handler function")
        return
    try:
        lang_func(curr_compile_lines, curr_compile_lines_label, rom_instructions, rom_instructions_label, args)
    except TypeError:
        print(f"[ERROR] Handler function has the wrong argument types, or count")


def instructions_to_rom_labels(curr_compile_lines_labels: list[str], rom_instructions_labels: list[(int | str, int | None | str, int | None)]):
    for line in curr_compile_lines_labels:
        m = re.match(r"[a-zA-Z][a-zA-Z0-9_-]+:", line)
        if line == '':
            continue
        if line.startswith('//'):
            rom_instructions_labels.append((line, None, None))
        if m is not None:
            rom_instructions_labels.append((m, None, None))
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
                    add_rom_instruction(inst_id, parts, rom_instructions_labels)
            else:
                print(f"[ERROR] Instruction \"{line}\" can not be resolved to a Native instruction after compiling,"
                      " exiting!")
                return False
    return True


def add_rom_instruction(inst_id, parts, rom_instructions_labels):
    if len(parts) > 2:
        rom_instructions_labels.append((inst_id, int(parts[1]), int(parts[2])))
    elif len(parts) > 1:
        rom_instructions_labels.append((inst_id, int(parts[1], 0)))
    else:
        rom_instructions_labels.append((inst_id, 0, 0))


def compile_file(file_path: str, args: CompilerArgs):
    file = open(file_path, "rt")

    if not file.readable():
        return

    lines = read_lines(file)

    for ind, val in enumerate(lines):
        lines[ind] = val.lower().strip()

    imported_files: dict[str, list[str]] = {}

    if not get_imported_files(imported_files, lines, file_path):
        return

    for file, file_lines in imported_files.items():
        for file_line_no in range(len(file_lines)):
            file_lines[file_line_no] = file_lines[file_line_no].lower().strip()

    macros: dict[int, Macro] = {}
    for file, included_lines in imported_files.items():
        load_macros(macros, file, included_lines)

    load_macros(macros, file_path, lines)

    variable_memory_pos: dict[str, int] = {}
    if not get_var_memory_address(lines, variable_memory_pos, args):
        return

    curr_compile_lines: list[str] = []

    copy_lines_exclude_compiler_instructions(curr_compile_lines, lines)

    depth_limit = 1_000
    curr_depth = 0
    while not is_only_native_instructions(curr_compile_lines):
        curr_depth = curr_depth + 1
        if not resolve_macros(curr_compile_lines, macros):
            return
        if curr_depth >= depth_limit:
            print(f"[ERROR] recursive macro? encountered depth of {depth_limit} and still found unresolved macros.")
            return

    print("[INFO] Macros resolved")

    resolve_variables(curr_compile_lines, variable_memory_pos)
    print("[INFO] Variables resolved")

    curr_compile_lines_labels: list[str] = curr_compile_lines.copy()

    resolve_labels(curr_compile_lines)
    print("[INFO] Labels resolved")

    rom_instructions: list[(int, int, int)] = []
    rom_instructions_labels: list[(int | str, int | None, int | None)] = []
    instructions_to_rom(curr_compile_lines, rom_instructions)
    instructions_to_rom_labels(curr_compile_lines_labels, rom_instructions_labels)

    call_language_handler(curr_compile_lines, curr_compile_lines_labels, rom_instructions, rom_instructions_labels,
                          args)
