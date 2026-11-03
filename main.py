import ast
from pathlib import Path


def find_python_files(folder: str) -> list[Path]:
    root = Path(folder)
    files = []
    for path in root.rglob("*.py"):
        files.append(path)
    return files


def make_chunk(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    source: str,
    file: Path,
    class_name: str | None,
) -> dict:
    code = ast.get_source_segment(source, node)
    docstring = ast.get_docstring(node) or ""

    header = f"File: {file.name}\n"
    if class_name:
        header += f"Class: {class_name}\n"
        header += f"Function: {class_name}.{node.name}\n"
    else:
        header += f"Function: {node.name}\n"
    header += f"Description: {docstring}\n"

    return {
        "name": node.name,
        "class_name": class_name or "",
        "file": str(file),
        "start_line": node.lineno,
        "code": code,
        "text": header + "\n" + code,
    }


def extract_functions(file: Path) -> list[dict]:
    source = file.read_text(encoding="utf-8")
    tree = ast.parse(source)
    chunks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunks.append(make_chunk(node, source, file, None))
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunks.append(make_chunk(item, source, file, node.name))
    return chunks


def main() -> None:
    files = find_python_files("repos/requests/src")
    all_chunks = []
    for file in files:
        all_chunks.extend(extract_functions(file))

    print(f"Found {len(all_chunks)} functions in {len(files)} files.")

    if not all_chunks:
        print("No functions found.")
        return

    count = 0
    for chunk in all_chunks:
        line_count = len(chunk["code"].splitlines())
        if line_count >= 20:
            print(f"Name: {chunk['name']}")
            print(f"File: {chunk['file']} (line {chunk['start_line']})")
            print(f"Line count: {line_count}")
            count += 1
    print(f"Found {count} functions with 20 or more lines.")


if __name__ == "__main__":
    main()
