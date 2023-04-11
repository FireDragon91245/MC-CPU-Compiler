import sys
import os

import compiler


def list_format(to_format: list, format_str: str):
    return ', '.join([format_str]*len(to_format))


# Compiler settings and CPU specs
COMPILER_VERSION = "1.0-wip"
CONTRIBUTORS_CPU = [
    "FireDragon91245"
]
CONTRIBUTORS_COMPILER = {
    "FireDragon91245"
}
MEMORY_SIZE = 256
MEMORY_BLOCKS = 8



print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
print(f"Compiler version: {COMPILER_VERSION}\n")
print(f"Contributors CPU: {list_format(CONTRIBUTORS_CPU, '%')}")
print(f"Contributors Compiler: {list_format(CONTRIBUTORS_COMPILER, '%')}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")

if len(sys.argv) <= 1:
    print("No source file provided, exiting!")
    exit(0)

file_path = sys.argv[1]

if os.path.exists(file_path):
    compiler.compile_file(file_path)
else:
    print(f"Source file: \"{file_path}\" was not found, exiting!")
    exit(0)

