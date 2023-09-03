from pathlib import Path

from compiler_obj import LanguageTarget, CompilerArgs, CompilerResult


class MCCPUALL(LanguageTarget):

    def transpile(self, compile_lines: list[str], compile_lines_with_labels_comments: list[str],
                  rom_instructions: list[(int, int, int)],
                  rom_instructions_with_labels_comments: list[(int | str, int | None, int | None)], args: CompilerArgs, compiler_root_dir: Path) -> CompilerResult:
        with open(compiler_root_dir.joinpath(f"{args.out_file}.mccpu"), "w") as f:
            for cl in compile_lines_with_labels_comments:
                f.write(f"{cl}\n")
            f.write("// ROM Instructions\n")
            for ri in rom_instructions:
                f.write(f"// {ri}\n")
            f.write("// ROM Instructions LBL\n")
            for ril in rom_instructions_with_labels_comments:
                f.write(f"// {ril}\n")
            f.flush()
            f.close()
        return CompilerResult.ok()
