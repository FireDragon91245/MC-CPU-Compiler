import unittest
from compiler import NATIVE_INSTRUCTIONS, match_instruction, compile_file
from compiler_obj import CompilerArgs
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
        args = CompilerArgs("mccpu", 256, 8, 64, 16)
        path = ".\\test_programms\\"
        all_files = [f for f in glob.glob(path) if os.path.isfile(f)]


if __name__ == '__main__':
    unittest.main()
