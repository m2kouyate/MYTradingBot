import os
import ast


def list_dir_with_tree(base_path, prefix=""):
    for entry in sorted(os.listdir(base_path)):
        if entry.endswith(".pyc") or entry == "__pycache__":
            continue  # Пропускаем .pyc файлы и папку __pycache__

        full_path = os.path.join(base_path, entry)
        print(f"{prefix}├── {entry}")

        if os.path.isdir(full_path):
            list_dir_with_tree(full_path, prefix + "│   ")
        elif entry.endswith(".py"):
            show_classes_and_functions(full_path, prefix + "│   ")


def show_classes_and_functions(file_path, prefix):
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read(), filename=file_path)
        except SyntaxError:
            print(f"{prefix}[SyntaxError in {file_path}]")
            return

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            print(f"{prefix}├── (Function) {node.name}")
        elif isinstance(node, ast.ClassDef):
            print(f"{prefix}├── (Class) {node.name}")


if __name__ == "__main__":
    project_path = "."  # Путь к проекту
    print(project_path)
    list_dir_with_tree(project_path)
