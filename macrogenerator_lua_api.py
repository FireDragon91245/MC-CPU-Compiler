from pathlib import Path

from compiler_obj import CompilerArgs


class MacrogeneratorLuaCompilerAPI:

    def get_out_woking_dir(self):
        return Path(self.args.out_file).parent.absolute().name

    def get_compiler_target(self):
        return self.args.target_lang

    def __init__(self, args: CompilerArgs):
        self.args = args
