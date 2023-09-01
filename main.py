import sys
import os
import argparse

import compiler
from compiler_obj import CompilerArgs, CompilerErrorLevel


def list_format(to_format: list, format_str: str):
    return ', '.join(['%s'] * len(to_format)) % tuple(to_format)


parser = argparse.ArgumentParser(prog="MCCPU-Compiler", description="Compile MCCPU source file to target language")
parser.add_argument("-t", "--target", type=str, help="the target Language", default="mccpu",
                    required=False, dest="language")
parser.add_argument("-m", "--memory", type=int, help="the memory size in bytes", default=2 ** 8,
                    required=False, dest="memory")
parser.add_argument("-mb", "--memoryBlocks", type=int, help="the count of blocks the memory is divided in",
                    default=8, required=False, dest="blocks")
parser.add_argument("-s", "--stack", type=int, help="the size of the stack in bytes", default=2 ** 6,
                    required=False, dest="stack")
parser.add_argument("-r", "--registers", type=int, help="define how many registers are avaidable", default=32,
                    required=False, dest="registers")
parser.add_argument("-el", "--exitLevel", type=CompilerErrorLevel
                    , help="define at what error level the compiler should exit",
                    choices=[member for member in CompilerErrorLevel if member != CompilerErrorLevel.INFO],
                    default=CompilerErrorLevel.ERROR, required=False, dest="exitLevel")
parser.add_argument("file")

parsed = parser.parse_args(sys.argv[1:])
args = CompilerArgs(target_lang=parsed.language, mem_size=parsed.memory, stack_size=parsed.stack,
                    memory_blocks=parsed.blocks, register_count=parsed.registers, exit_level=parsed.exitLevel)

# Compiler settings and CPU specs
COMPILER_VERSION = "1.0-wip"
CONTRIBUTORS_CPU = [
    "FireDragon91245"
]
CONTRIBUTORS_COMPILER = [
    "FireDragon91245"
]

print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
print(f"Compiler version: {COMPILER_VERSION}\n")
print(f"Contributors CPU: {list_format(CONTRIBUTORS_CPU, '%')}")
print(f"Contributors Compiler: {list_format(CONTRIBUTORS_COMPILER, '%')}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")

if len(sys.argv) <= 1:
    print("No source file provided, exiting!")
    exit(0)

if os.path.exists(parsed.file):
    compiler.compile_file(parsed.file, args)
else:
    print(f"Source file: \"{parsed.file}\" was not found, exiting!")
    exit(0)
