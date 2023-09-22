import re
import unittest

from compiler import resolve_args, TYPE_REGEX_MATCH_REPLACERS, resolve_macro, \
    resolve_macros, load_macros, copy_lines_exclude_compiler_instructions
from objects.CompilerErrorLevels import CompilerErrorLevels
from objects.MacroTypes import MacroTypes
from objects.Macro import Macro
from tests.test_data import EXAMPLE_COMP_ARGS


class MacroTests(unittest.TestCase):
    def test_macro_arg_resolve(self):
        mac = Macro("test %register, %register", "", [MacroTypes.REGISTER, MacroTypes.REGISTER], ["mov %1, %2"], [],
                    False, False, None, "test", 0)
        res = resolve_args("mov %1, %2", re.match(
            f'test {TYPE_REGEX_MATCH_REPLACERS["%register"]}, {TYPE_REGEX_MATCH_REPLACERS["%register"]}',
            "test &r1, &r2"), mac, 0, {})
        self.assertEqual(res, "mov &r1, &r2", "macro arg resolver contains errors")

    def test_macro_resolve(self):
        mac = Macro("zero %register", "", [MacroTypes.REGISTER], ["mov %1, 0x00"], [], False, False, None, "test", 0)
        lines = ["zero &r1"]
        res = resolve_macro(lines, 0, mac, 0, [mac], {}, EXAMPLE_COMP_ARGS)
        self.assertEqual(res.status, CompilerErrorLevels.OK, str(res))
        self.assertEqual(lines, ["mov &r1, 0x00"])

    def test_macro_resolve_memory_address_lookup(self):
        mac = Macro("test %register, %register", "", [MacroTypes.REGISTER, MacroTypes.REGISTER], ["mov %1, %2"], [],
                    False, False, None, "test", 0)
        res = resolve_args("mov %1, [%2]", re.match(
            f'test {TYPE_REGEX_MATCH_REPLACERS["%register"]}, {TYPE_REGEX_MATCH_REPLACERS["%variable"]}',
            "test &r1, *myvar"), mac, 0, {"myvar": 20})
        self.assertEqual(res, "mov &r1, 20", "macro arg resolver contains errors")

    def test_macros_resolve(self):
        mac = Macro("zero %register", "", [MacroTypes.REGISTER], ["mov %1, 0x00"], [], False, False, None, "test", 0)
        lines = ["zero &r1"]
        res = resolve_macros(lines, {0: mac}, {}, EXAMPLE_COMP_ARGS)
        self.assertEqual(res.status, CompilerErrorLevels.OK, str(res))
        self.assertEqual(lines, ["mov &r1, 0x00"])

    def test_load_macro(self):
        macros = {}
        lines = [
            "#macro zero %register",
            "mov %1, 0x00",
            "#endmacro"
        ]
        res = load_macros(macros, "tests", lines, {})
        self.assertEqual(res.status, CompilerErrorLevels.OK, str(res))
        self.assertEqual(len(macros), 1, "no macros were loaded")
        self.assertTrue(macros[list(macros.keys())[-1]].__cmp__(
            Macro("zero %register", "", [MacroTypes.REGISTER], ["mov %1, 0x00"], [], False, False, None, "test", 0)),
                        "macro loading error, wrong macro loaded")

    def test_exclude_comp_instr(self):
        lines = [
            "#macro zero %register",
            "mov %1, 0x00",
            "#endmacro",
            "zero &r1"
        ]
        complines = []
        res = copy_lines_exclude_compiler_instructions(complines, lines)
        self.assertEqual(res.status, CompilerErrorLevels.OK, str(res))
        self.assertEqual(complines, ["zero &r1"])


if __name__ == '__main__':
    unittest.main()
