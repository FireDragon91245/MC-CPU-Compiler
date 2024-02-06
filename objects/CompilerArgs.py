from objects.CompilerErrorLevels import CompilerErrorLevels


class CompilerArgs:

    def __init__(self, target_lang: str, mem_size: int, memory_blocks: int, stack_size: int, register_count: int,
                 exit_level: CompilerErrorLevels, out_file: str) -> None:
        self.out_file = out_file
        self.exit_level = exit_level
        self.register_count = register_count
        self.memory_blocks = memory_blocks
        self.mem_size = mem_size
        self.target_lang = target_lang
        self.stack_size = stack_size
