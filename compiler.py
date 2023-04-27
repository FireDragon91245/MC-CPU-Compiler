from compiler_obj import MacroTypes, MemoryManagementType, Macro
import re
import os

# %number can be equal to %label, only the compiler deals with %label & %variable and is resolved to %number at
# compile time
NATIVE_INSTRUCTIONS = [
    "ADD %register, %register",  # reg a + reg b (Updates Zero, Overflow CPU flags)
    "SUB %register, %register",  # reg a - reg b (Updates Zero, Overflow CPU flags)
    "DIV %register, %register",  # reg a / reg b (Updates Zero, Overflow CPU flags)
    "MULT %register, %register",  # reg a * reg b (Updates Zero, Overflow CPU flags)
    "INC %register",  # reg a++ (Updates Overflow CPU flag)
    "DEC %register",  # reg a-- (Updates Zero, Overflow CPU flags)
    "CALL %number",  # JMP + PUSH number a
    "RET",  # POP + JMP upper stack
    "JMP %label",
    "JMPZ %label",  # jump if Zero CPU flag is set
    "JMPS %label",  # jump if Smaller CPU flag is set
    "JMPB %label",  # jump if Bigger CPU flag is set
    "JMPE %label",  # jump if Equal CPU flag is set
    "CMP %register, %register",  # reg a == > < reg b (Updates Smaller, Bigger, Zero, Equal CPU flags)
    "PUSH %register",  # PUSH + INC stack ptr
    "POP %register",  # POP + DEC stack ptr
    "CPY %register, %register",
    "LOAD %register, %number",
    "MCPY %address, %address",
    "MLOAD %address, %number",
    "MGET %register, %address",
    "MSET %address, %register",
    "AND %register, %register",  # (Updates Zero CPU flag)
    "OR %register, %register",  # (Updates Zero CPU flag)
    "NOT %register",  # (Updates Zero CPU flag)
    "SHL %register",  # shift left (Updates Zero CPU flag)
    "SHR %register",  # shift right (Updates Zero CPU flag)
    "NOP",  # no operation
    "HALT",  # disables RUNNING CPU flag and halts the cpu (RUNNING CPU flag is only enabled by the start button in MC)
]
TYPE_REGEX_MATCH_REPLACERS = {
    "%register": "(&r[0-9]{1,3})",
    "%number": "(0x[0-9A-Fa-f]{1,2}|[0-9]{1,3})",
    "%address": r"(\*0x[0-9A-Fa-f]{1,2}|\*[0-9]{1,3})",
    "%variable": r"(\*[a-zA-Z][a-zA-Z0-9]*)",
    "%label": "(~[a-zA-Z][a-zA-Z0-9_-]*)",
}


def read_lines(file):
    return file.read().splitlines()


def get_memory_management_type_static(line, line_no):
    if line.find("auto") != -1:
        if line.find("incremental") != -1:
            return MemoryManagementType.AUTO_STATIC_INCREMENTAL
        elif line.find("balanced") != -1:
            return MemoryManagementType.AUTO_STATIC_BALANCED
        else:
            print(
                f"[WARN] #memorylayout [static auto] section at ln<{line_no}> did not contain a memory balancing type "
                f"[incremental / balanced] defaulting to [incremental]")
            return MemoryManagementType.AUTO_STATIC_INCREMENTAL
    else:
        if line.find("incremental") != -1:
            return MemoryManagementType.STATIC_INCREMENTAL
        elif line.find("balanced") != -1:
            return MemoryManagementType.STATIC_BALANCED
        else:
            print(
                f"[WARN] #memorylayout [static] section at ln<{line_no}> did not contain a memory balancing type ["
                f"incremental / balanced] defaulting to [incremental]")
            return MemoryManagementType.STATIC_INCREMENTAL


def get_memory_management_type(lines):
    for line_no, line in enumerate(lines):
        if line.startswith("#"):
            if line.find("memorylayout") != -1:
                if line.find("static") != -1:
                    return get_memory_management_type_static(line, line_no)
                elif line.find("explicit") != -1:
                    return MemoryManagementType.EXPLICIT
                else:
                    print(
                        f"[WARN] #memorylayout at ln<{line_no}> does not contain a valid variable layout type token ["
                        f"static / static auto / explicit] + address balancing type [incremental / balanced] "
                        f"continuing search for other #memorylayout sections")
    print(
        "[WARN] No #memorylayout section found or no valid variable layout type token found [static / static auto / "
        "explicit] + address balancing type [incremental / balanced] defaulting to [static auto incremental]")
    return MemoryManagementType.AUTO_STATIC_INCREMENTAL


def find_static_memory_layout_balanced(variable_memory_pos, lines):
    memory_space = 256
    memory_bank_index = [
        0,
        32,
        64,
        96,
        128,
        160,
        192,
        224
    ]
    curr_memory_bank = 0


def find_static_memory_layout_incremental(variable_memory_pos: dict, lines):
    curr_line = 0
    memory_space = 256
    memory_index = 0
    for line_no, line in enumerate(lines):
        if line.startswith("#"):
            if line.find("memorylayout") != -1:
                curr_line = line_no + 1

    while curr_line < lines.count():
        if lines[curr_line].startswith("#"):
            if lines[curr_line].find("end") != 1 and line[curr_line].find("memorylayout") != 1:
                break

        variable_memory_pos.update({memory_index: lines[curr_line].strip()})
        memory_index = memory_index + 1

        if memory_index >= memory_space:
            print("[ERROR] out of memory addresses, exiting")
            return

        curr_line = curr_line + 1


def find_static_auto_memory_balanced(variable_memory_pos, lines):
    pass


def find_static_auto_memory_incremental(variable_memory_pos: dict[str, int], lines: list[str]):
    memory_space = 256
    memory_index = 0
    var_match = r"\*[a-zA-Z]+"
    for line_no, line in enumerate(lines):
        matches: list[str] = re.findall(var_match, line)
        for match in matches:
            if variable_memory_pos.get(match.lstrip('*')) is None:
                variable_memory_pos.update({match.lstrip('*'): memory_index})
                memory_index = memory_index + 1

                if memory_index >= memory_space:
                    print("[ERROR] out of memory addresses, exiting")
                    return


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
                                f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value \"{line}\" was not found, exiting!")
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
                                f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value \"{line}\" was not found exiting!")
                            return False
                        if imported_files.get(match) is not None:
                            continue
                        imported_files[match] = read_lines(file)
                        get_imported_files(imported_files, imported_files.get(match), curr_dir + match)
                    else:
                        print(
                            f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file.name}\" with value \"{line}\" was not found exiting!")
                        return False
    return True


def get_macro_arg_types(macro_opener, file, line_no) -> list[MacroTypes]:
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
                f"[ERROR] macro \"{macro_opener}\" in file \"{file}\" at line <{line_no}> used not valid type \"{match}\" valid are [%label, %variable, %address, %number, %register]")
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
                try:
                    groups = macro_end_matches.groups()
                except:
                    pass
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
        for inst in NATIVE_INSTRUCTIONS:
            if match_instruction(inst.lower(), line):
                found = True
                break
        if not found:
            return False
    return True


def resolve_args(macro_line, args, macro: Macro, macro_id: int):
    for i in range(0, len(args.groups())):
        macro_line = macro_line.replace(f"%{i + 1}", args.group(i+1)).replace("%__macro_id", str(macro_id)).\
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


def resolve_macros(curr_compile_lines: list[str], variables: dict[str, int], macros: dict[int, Macro]) -> bool:
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
        for inst in NATIVE_INSTRUCTIONS:
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
                f"[ERROR] can not resolve instruction \"{curr_compile_lines[line_no]}\" to any macro or std instruction")
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
            while not lines[line_no].startswith("#enmemorylayout"):
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
                        curr_compile_lines[i] = curr_compile_lines[i].replace("~" + matches.group(1), f"{instruction_no}")
                    break
        if not found:
            break
    if not curr < max_iter:
        print(f"[ERROR] Internal compiler error to many labels max of {max_iter} reached")
        return False
    return True


def compile_file(file_path: str):
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

    memory_management_type = get_memory_management_type(lines)

    curr_compile_lines: list[str] = []

    variable_memory_pos: dict[str, int] = {}
    if memory_management_type == MemoryManagementType.STATIC_BALANCED:
        find_static_memory_layout_balanced(variable_memory_pos, lines)
    elif memory_management_type == MemoryManagementType.STATIC_INCREMENTAL:
        find_static_memory_layout_incremental(variable_memory_pos, lines)
    elif memory_management_type == MemoryManagementType.AUTO_STATIC_BALANCED:
        find_static_auto_memory_balanced(variable_memory_pos, lines)
    elif memory_management_type == MemoryManagementType.AUTO_STATIC_INCREMENTAL:
        find_static_auto_memory_incremental(variable_memory_pos, lines)

    copy_lines_exclude_compiler_instructions(curr_compile_lines, lines)

    depth_limit = 1_000
    curr_depth = 0
    while not is_only_native_instructions(curr_compile_lines):
        curr_depth = curr_depth + 1
        if not resolve_macros(curr_compile_lines, variable_memory_pos, macros):
            return
        if curr_depth >= depth_limit:
            print(f"[ERROR] recursive macro? encountered depth of {depth_limit} and still found unresolved macros.")
            return

    print("[INFO] Macros resolved, the resolved code will be saved to out.mccpu")

    resolve_labels(curr_compile_lines)

    print("[INFO] Labels resolved")

    write_file("out.mccpu", curr_compile_lines)
