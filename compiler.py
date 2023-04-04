import enum
import re

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
            print(f"[WARN] #memorylayout [static auto] section at ln<{line_no}> did not contain a memory balancing type [incremental / balanced] defaulting to [incremental]")
            return MemoryManagementType.AUTO_STATIC_INCREMENTAL
    else:
        if line.find("incremental") != -1:
            return MemoryManagementType.STATIC_INCREMENTAL
        elif line.find("balanced") != -1:
            return MemoryManagementType.STATIC_BALANCED
        else:
            print(f"[WARN] #memorylayout [static] section at ln<{line_no}> did not contain a memory balancing type [incremental / balanced] defaulting to [incremental]")
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
                    print(f"[WARN] #memorylayout at ln<{line_no}> does not contain a valid variable layout type token [static / static auto / explicit] + address balancing type [incremental / balanced] continuing search for other #memorylayout sections")
    print("[WARN] No #memorylayout section found or no valid variable layout type token found [static / static auto / explicit] + address balancing type [incremental / balanced] defaulting to [static auto incremental]")
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


def compile_file(file_path: str):
    file = open(file_path, "rt")

    if not file.readable():
        return CompilerResult("Not Readable", "File to compile was not readable!")

    lines = read_lines(file)

    for ind, val in enumerate(lines):
        lines[ind] = val.lower()

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


class CompilerResult:

    def __init__(self, error_short, error_reason):
        self.error_short = error_short
        self.error_reason = error_reason


class MemoryManagementType(enum):
    STATIC_INCREMENTAL = 1
    EXPLICIT_INCREMENTAL = 2
    AUTO_STATIC_INCREMENTAL = 3
    STATIC_BALANCED = 4
    EXPLICIT_BALANCED = 5
    AUTO_STATIC_BALANCED = 6
