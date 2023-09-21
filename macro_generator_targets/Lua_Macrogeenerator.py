from compiler_obj import MacroGenerator, Macro, CompilerArgs, CompilerResult
import lupa.lua54 as lupa


class Lua(MacroGenerator):
    def use_generator(self, args: CompilerArgs, macro: Macro, macro_args: list[str]):
        if self.on_macro_usage is None:
            return CompilerResult.error("[ERROR][LUA] Failed to use lua generator (macro used caled before macro load)")
        try:
            self.on_macro_usage(args, macro, macro_args)
        except Exception as e:
            return CompilerResult.error(f"[ERROR][LUA] Failed to use lua generator (Lua Error): {e}")

    @staticmethod
    def get_target_language() -> str:
        return "lua"

    def __init__(self, generator_lines: list[str]) -> None:
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
                if generator is None or lupa.lua_type(generator) != "table":
                    return CompilerResult.error("[ERROR][LUA] Failed to load lua generator (Not a table returned)")
                if generator.onAfterMacroLoad is None or lupa.lua_type(generator.onAfterMacroLoad) != "function":
                    return CompilerResult.error("[ERROR][LUA] Failed to load lua generator (onAfterMacroLoad not a "
                                                "function or undefined)")
                if generator.onMacroUsage is None or lupa.lua_type(generator.onMacroUsage) != "function":
                    return CompilerResult.error("[ERROR][LUA] Failed to load lua generator (onMacroUsage not a "
                                                "function or undefined)")
                generator.onAfterMacroLoad(args, macro)
                self.on_macro_usage = generator.onMacroUsage
            except Exception as e:
                return CompilerResult.error(f"[ERROR][LUA] Failed to load lua generator (Lua Error): {e}")
        else:
            return CompilerResult.error("[ERROR][LUA] Failed to load lua generator")
