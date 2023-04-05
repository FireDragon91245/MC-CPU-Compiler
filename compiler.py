from compiler_obj import MacroTypes, MemoryManagementType, Macro
import re
import os


def read_lines(file):
    lines = []
    for line in file:
        lines.append(line)
    return lines


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
    include_match = r"<([a-z|0-9|A-Z]+)>"
    for line_no, line in enumerate(lines):
        if line.startswith('#'):
            if line.find("includemacrofile") != -1:
                matches: list[str] = re.findall(include_match, line)
                for match in matches:
                    curr_dir = os.getcwd()
                    if os.path.isfile(curr_dir + "/macrodefs/" + match + ".mccpu"):
                        file = open(curr_dir + "/macrodefs/" + match + ".mccpu")
                        if not file.readable():
                            print(
                                f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file}\" with value \"{line}\" was not found, exiting!")
                            return False
                        if imported_files.get(match) is not None:
                            continue
                        imported_files[match] = read_lines(file)
                        get_imported_files(imported_files, imported_files.get(match), curr_dir + "/macrodefs/" + match + ".mccpu")
                    elif os.path.isfile(curr_dir + match):
                        file = open(curr_dir + match)
                        if not file.readable():
                            print(
                                f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file}\" with value \"{line}\" was not found exiting!")
                            return False
                        if imported_files.get(match) is not None:
                            continue
                        imported_files[match] = read_lines(file)
                        get_imported_files(imported_files, imported_files.get(match), curr_dir + match)
                    else:
                        print(
                            f"[ERROR] #Includemacrofile on line <{line_no}> in file \"{file}\" with value \"{line}\" was not found exiting!")
                        return False
    return True


def get_macro_arg_types(macro_opener, file, line_no) -> list[MacroTypes]:
    type_reg = r"%[a-zA-Z]*"
    matches: list[str] = re.findall(type_reg, macro_opener)
    macro_types: list[MacroTypes] = {}
    for match in matches:
        if match is "%label":
            macro_types.append(MacroTypes.LABEL)
        elif match is "%variable":
            macro_types.append(MacroTypes.VARIABLE)
        elif match is "%address":
            macro_types.append(MacroTypes.MEMORY_ADDRESS)
        elif match is "%number":
            macro_types.append(MacroTypes.NUMBER)
        elif match is "%register":
            macro_types.append(MacroTypes.REGISTER)
        else:
            print(f"[ERROR] macro \"{macro_opener}\" in file \"{file}\" at line <{line_no}> used not valid type \"{match}\" valid are [%label, %variable, %address, %number, %register]")
            return None
    return macro_types


def load_macros(macros, file, lines: list[str]):
    macro_reg = r"#\s*macro\s*(.+)"
    macro_end_reg = r"(#\s*macroend\s*)(.+)?"
    macro_reg_com = re.compile(macro_reg)
    macro_end_reg_com = re.compile(macro_end_reg)
    lines_iter = enumerate(lines)
    for line_no, line in lines_iter:
        matches = macro_reg_com.match(line)
        if len(matches.groups()) >= 1:
            macro_opener = matches.group(0)
            macro_args = get_macro_arg_types(macro_opener, file, line_no)
            if macro_args is None:
                return False
            macro_top: list[str] = []
            macro_bottom: list[str] = []
            complex_macro = False
            currently_macro_top = True
            macro_start_line_no = line_no
            while True:
                line_no, line = next(lines_iter, None)
                macro_end_matches = macro_end_reg_com.match(line)
                if line is None:
                    print(f"[ERROR] Expected #endmacro after #macro in file \"{file}\" at line <{macro_start_line_no}>")
                    return False
                if line is "...":
                    complex_macro = True
                    currently_macro_top = False
                elif len(macro_end_matches.groups()) >= 1:
                    if complex_macro:
                        if not (len(macro_end_matches.groups()) >= 2):
                            print(f"[ERROR] Complex macros (macros using \"...\") need to have a closing expression "
                                  f"error at #endmacro in file \"{file}\" at line <{line_no}>")
                            return False
                        macros[abs(hash(macro_opener))] = Macro(macro_opener, macro_end_matches.group(1), macro_args, macro_top,
                                                                macro_bottom, complex_macro)
                    else:
                        if len(macro_end_matches.groups()) == 1:
                            macros[abs(hash(macro_opener))] = Macro(macro_opener, "", macro_args, macro_top, macro_bottom, complex_macro)
                        else:
                            macros[abs(hash(macro_opener))] = Macro(macro_opener, macro_end_matches.group(1),
                                                                    macro_args, macro_top,
                                                                    macro_bottom, complex_macro)
                    break
                else:
                    if currently_macro_top:
                        macro_top.append(line)
                    else:
                        macro_bottom.append(line)
    return True


            




def compile_file(file_path: str):
    file = open(file_path, "rt")

    if not file.readable():
        return

    lines = read_lines(file)

    for ind, val in enumerate(lines):
        lines[ind] = val.lower()

    imported_files: dict[str, list[str]] = {}

    if not get_imported_files(imported_files, lines, file_path):
        return

    for file, lines in imported_files.items():
        print(file)

    macros: dict[int, Macro] = {}
    for file, included_lines in imported_files.items():
        load_macros(macros, file, included_lines)

    load_macros(macros, file_path, lines)

    memory_management_type = get_memory_management_type(lines)

    variable_memory_pos = {}
    if memory_management_type == MemoryManagementType.STATIC_BALANCED:
        find_static_memory_layout_balanced(variable_memory_pos, lines)
    elif memory_management_type == MemoryManagementType.STATIC_INCREMENTAL:
        find_static_memory_layout_incremental(variable_memory_pos, lines)
    elif memory_management_type == MemoryManagementType.AUTO_STATIC_BALANCED:
        find_static_auto_memory_balanced(variable_memory_pos, lines)
    elif memory_management_type == MemoryManagementType.AUTO_STATIC_INCREMENTAL:
        find_static_auto_memory_incremental(variable_memory_pos, lines)