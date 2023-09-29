from enum import Enum


class ArgumentSize(Enum):
    BYTE = 1
    SBYTE = 2
    WORD = 3
    SWORD = 4
    DWORD = 5
    SDWORD = 6
    QWORD = 7
    SQWORD = 8
    TBYTE = 9
    REAL4 = 10
    REAL8 = 11
    REAL10 = 12

    # byte size signed info [0] = byte size [1] = signed
    size_bss_info: dict['ArgumentSize', (int, bool)] = {
        BYTE: (1, False),
        SBYTE: (1, True),
        WORD: (2, False),
        SWORD: (2, True),
        DWORD: (4, False),
        SDWORD: (4, True),
        QWORD: (8, False),
        SQWORD: (8, True),
        REAL4: (4, True),
        REAL8: (8, True),
    }

    def __getitem__(self, item: 'ArgumentSize') -> (int, bool):
        return self.size_bss_info[item]

    @staticmethod
    def get_size(size: 'ArgumentSize') -> int:
        return ArgumentSize.size_bss_info[size][0]

    @staticmethod
    def is_signed(size: 'ArgumentSize') -> bool:
        return ArgumentSize.size_bss_info[size][1]
