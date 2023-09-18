import unittest
from compiler import NATIVE_INSTRUCTIONS, match_instruction, compile_file
from compiler_obj import CompilerArgs, CompilerErrorLevels
from test_data import EXAMPLE_STD_INSTRUCTIONS
import glob
import os


class InstructionTest(unittest.TestCase):
    def test_match_instructions(self):
        self.assertTrue(any(list(match_instruction(x, x) for x in NATIVE_INSTRUCTIONS)))

    def test_match_instructions_example(self):
        for instruction in EXAMPLE_STD_INSTRUCTIONS:
            self.assertTrue(any(list(match_instruction(x, instruction) for x in NATIVE_INSTRUCTIONS)),
                            f"Failed to match instruction: {instruction} to any native instruction")

    def test_example_programms(self):
        path = ".\\test_programms\\*"
        all_files = [f for f in glob.glob(path) if os.path.isfile(f)]
        for file in all_files:
            if file.find("ignore") != -1:
                continue
            args = CompilerArgs("MCCPU", 256, 8, 64, 16, CompilerErrorLevels.WARNING,
                                f"test_out\\{os.path.splitext(os.path.basename(file))[0]}")
            res = compile_file(file, args)
            self.assertTrue(res.status == CompilerErrorLevels.OK, str(res))


if __name__ == '__main__':
    unittest.main()
