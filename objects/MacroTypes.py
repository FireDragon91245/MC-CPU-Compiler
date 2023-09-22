from enum import Enum


class MacroTypes(Enum):
    LABEL = 1
    VARIABLE = 2
    MEMORY_ADDRESS = 3
    NUMBER = 4
    REGISTER = 5
    REGISTER_POINTER = 6
    STRING = 7
