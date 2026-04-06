import ast
import os
from pathlib import Path

wire_name = "dependency_injector.wiring"


def find_wiring_modules():
    modules = []
    file_paths = get_file_paths([Path("src")])
    for file_path in file_paths:
        with open(file_path, encoding='utf-8') as file:
            text = file.read()
            p = ast.parse(text)
            for node in ast.walk(p):
                if hasattr(node, "module") and node.module == wire_name:
                    modules.append(file_path.split(".py")[0].replace(os.sep,"."))
                    break

    return modules


def get_file_paths(paths: list[Path]) -> list[str]:
    files_to_check = []
    while paths:
        path = paths.pop()
        for entry in path.iterdir():
            if entry.is_file() and str(entry).endswith(".py"):
                files_to_check.append(str(entry))
            elif entry.is_dir():
                paths.append(entry)
    return files_to_check