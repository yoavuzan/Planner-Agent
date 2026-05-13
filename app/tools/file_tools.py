import os
from pathlib import Path
from langchain_core.tools import tool

BASE_DIR = Path("workspace").resolve()
BASE_DIR.mkdir(exist_ok=True)

def is_safe_path(full_path: Path) -> bool:
    return str(full_path.resolve()).startswith(str(BASE_DIR))

@tool
def write_file(path: str, content: str) -> str:
    """Write a file inside the workspace directory."""
    full_path = (BASE_DIR / path).resolve()

    if not is_safe_path(full_path):
        return "Error: Access denied. Path is outside workspace."

    os.makedirs(full_path.parent, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return f"Successfully created: {path}"

@tool
def read_file(path: str) -> str:
    """Read a file from the workspace."""
    full_path = (BASE_DIR / path).resolve()

    if not is_safe_path(full_path):
        return "Error: Access denied."

    if not full_path.exists():
        return f"Error: File '{path}' not found."

    return full_path.read_text(encoding="utf-8")

@tool
def list_files(path: str = ".") -> str:
    """List all files in a directory within the workspace."""
    full_path = (BASE_DIR / path).resolve()

    if not is_safe_path(full_path):
        return "Error: Access denied."

    if not full_path.exists():
        return f"Error: Path '{path}' does not exist."

    files = [str(p.relative_to(BASE_DIR)) for p in full_path.rglob("*")]
    return "\n".join(files) if files else "Directory is empty."


if __name__ == "__main__":
    print(
        write_file.invoke({
            "path": "example.txt",
            "content": "Hello, World!"
        })
    )

    print(
        read_file.invoke({
            "path": "example.txt"
        })
    )

    print(list_files.invoke({}))