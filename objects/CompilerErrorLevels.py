from enum import Enum


class CompilerErrorLevels(Enum):
    INFO = 1
    OK = 2
    WARNING = 3
    ERROR = 4
    NONE = 5

    def is_severity_higher(self, other):
        return self.value > other.value
