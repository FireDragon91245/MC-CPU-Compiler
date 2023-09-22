from objects.MacroGenerator import MacroGenerator
from objects.MacroTypes import MacroTypes


class Macro:

    def __init__(self, macro_opener: str, macro_closer: str, macro_args: list[MacroTypes], macro_top: list[str],
                 macro_bottom: list[str], complex_macro: bool, generated_macro: bool,
                 macro_generator: MacroGenerator | None, file: str, macro_start_line_no: int) -> None:
        self.macro_start_line_no = macro_start_line_no
        self.file = file
        self.macro_generator = macro_generator
        self.generated_macro = generated_macro
        self.complex_macro = complex_macro
        self.macro_bottom = macro_bottom
        self.macro_top = macro_top
        self.macro_args = macro_args
        self.macro_closer = macro_closer
        self.macro_opener = macro_opener
        self.macro_no = 0

    def __cmp__(self, other):
        return self.complex_macro == other.complex_macro and self.macro_bottom == other.macro_bottom and\
            self.macro_top == other.macro_top and self.macro_args == other.macro_args and\
            self.macro_closer == other.macro_closer and self.macro_opener == other.macro_opener and\
            self.macro_generator == other.macro_generator and self.generated_macro == other.generated_macro
