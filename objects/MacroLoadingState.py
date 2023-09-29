from objects.ArgumentTypes import ArgumentTypes
from objects.MacroGenerator import MacroGenerator


class MacroLoadingState:
    def __init__(self, macro_opener: str, file: str, macro_start_line_no: int):
        self.macro_generator: MacroGenerator | None = None
        self.generated_macro: bool = False
        self.macro_bottom: list[str] = []
        self.macro_top: list[str] = []
        self.macro_args: list[ArgumentTypes] = []
        self.macro_end: str | None = None
        self.macro_opener: str = macro_opener
        self.complex_macro: bool = False
        self.currently_macro_top: bool = True
        self.macro_generator_start: int = 0
        self.file: str = file
        self.macro_generator_lang: str = ""
        self.macro_start_line_no = macro_start_line_no
        self.macro_id: int | None = None
