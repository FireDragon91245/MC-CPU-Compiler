from objects.MacroGenerator import MacroGenerator
from objects.CompilerResult import CompilerResult
from objects.CompilerArgs import CompilerArgs
from objects.MacroTypes import MacroTypes
from objects.Macro import Macro
import lupa.lua54 as lupa

MACRO_LOAD_FUNC_NAME = "onAfterMacroLoad"

MACRO_USE_FUNC_NAME = "onMacroUse"


class LuaMacroGeneratorArgsWrapper:
    def __init__(self, macro_args_type: list[MacroTypes], macro_args_value: list[str]):
        self.macro_args_type = macro_args_type
        self.macro_args_value = macro_args_value

    def get_macro_arg_types(self):
        return [str(t) for t in self.macro_args_type]

    def get_macro_arg_values(self):
        return self.macro_args_value

    def get_macro_arg(self, index: int):
        return self.macro_args_value[index]

    def __getitem__(self, item):
        return self.macro_args_value[item - 1]


class LuaMacroGeneratorMacroWrapper:
    def __init__(self, macro: Macro):
        self.macro = macro

    def get_macro_signature(self):
        return self.macro.macro_opener

    def is_complex_macro(self):
        return self.macro.complex_macro

    def is_generated_macro(self):
        return self.macro.generated_macro

    def make_complex_macro(self):
        self.macro.complex_macro = True

    def make_simple_macro(self):
        self.macro.complex_macro = False

    def clear_macro_top(self):
        self.macro.macro_top = []

    def clear_macro_bottom(self):
        self.macro.macro_bottom = []

    def add_macro_top(self, line: str):
        self.macro.macro_top.append(line)

    def add_macro_bottom(self, line: str):
        self.macro.macro_bottom.append(line)


class LuaMacroGeneratorCompilerWrapper:
    def __init__(self, comp_args: CompilerArgs):
        self.comp_args = comp_args

    @staticmethod
    def ok():
        return CompilerResult.ok()


class Lua(MacroGenerator):
    def use_generator(self, args: CompilerArgs, macro: Macro, macro_args: list[str]):
        if self.on_macro_usage is None:
            return CompilerResult.error("[ERROR][LUA] Failed to use lua generator"
                                        " (macro used called before macro load)")
        try:
            return self.on_macro_usage(self.generator_table, LuaMacroGeneratorCompilerWrapper(args),
                                       LuaMacroGeneratorMacroWrapper(macro),
                                       LuaMacroGeneratorArgsWrapper(macro.macro_args,
                                                                    macro_args)) or CompilerResult.ok()
        except Exception as e:
            return CompilerResult.error(f"[ERROR][LUA] Failed to use lua generator (Lua Error): {type(e)}{e}")

    @staticmethod
    def get_target_language() -> str:
        return "lua"

    def __init__(self, generator_lines: list[str]) -> None:
        self.generator_table = None
        self.on_macro_usage = None
        self.generator_lines = generator_lines
        self.lua_runtime = lupa.LuaRuntime()
        self.lua_runtime.globals()["print"] = print

    @staticmethod
    def merge_lines(lines: list[str]) -> str:
        return "\n".join(lines)

    def load_generator(self, args: CompilerArgs, macro: Macro) -> CompilerResult:
        res = self.lua_runtime.compile(Lua.merge_lines(self.generator_lines))
        if lupa.lua_type(res) == "function":
            try:
                generator = res()
                print(generator)
                if generator is None or lupa.lua_type(generator) != "table":
                    return CompilerResult.error("[ERROR][LUA] Failed to load lua generator (Not a table returned)")
                if generator[MACRO_LOAD_FUNC_NAME] is None or \
                        lupa.lua_type(generator[MACRO_LOAD_FUNC_NAME]) != "function":
                    return CompilerResult.error("[ERROR][LUA] Failed to load lua generator (onAfterMacroLoad not a "
                                                "function or undefined)")
                if generator[MACRO_USE_FUNC_NAME] is None or \
                        lupa.lua_type(generator[MACRO_USE_FUNC_NAME]) != "function":
                    return CompilerResult.error("[ERROR][LUA] Failed to load lua generator (onMacroUse not a "
                                                "function or undefined)")
                generator[MACRO_LOAD_FUNC_NAME](generator, LuaMacroGeneratorCompilerWrapper(args),
                                                LuaMacroGeneratorMacroWrapper(macro))
                self.generator_table = generator
                self.on_macro_usage = generator[MACRO_USE_FUNC_NAME]
            except Exception as e:
                return CompilerResult.error(f"[ERROR][LUA] Failed to load lua generator (Lua Error): {type(e)}{e}")
        else:
            return CompilerResult.error("[ERROR][LUA] Failed to load lua generator")
