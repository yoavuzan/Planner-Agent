import os
from pathlib import Path
from langchain_core.tools import tool

BASE_DIR = Path("workspace").resolve()
BASE_DIR.mkdir(exist_ok=True)


def is_safe_path(full_path: Path) -> bool:
    return str(full_path.resolve()).startswith(str(BASE_DIR))


@tool
def write_file(path: str, content: str, append: bool = True) -> str:
    """
    Write content to a file in the workspace.
    By default (append=True), it appends to the file if it exists.
    Set append=False to overwrite the file.
    If the file does not exist, it will be created.
    """
    if not path or path.strip() in ["", "/", "."]:
        return "Error: Invalid path. Please provide a filename."

    # Strip leading slashes to keep paths relative to BASE_DIR
    clean_path = path.lstrip("/\\")
    full_path = (BASE_DIR / clean_path).resolve()

    if not is_safe_path(full_path):
        return f"Error: Access denied. Path '{path}' is outside workspace."

    os.makedirs(full_path.parent, exist_ok=True)
    
    # Decide mode: 'a' for append, 'w' for overwrite
    # Use 'a' only if file exists AND append is True
    mode = "a" if (full_path.exists() and append) else "w"
    
    with open(full_path, mode, encoding="utf-8") as f:
        f.write(content)
    
    status = "appended to" if mode == "a" else "created/overwritten"
    return f"Successfully {status}: {clean_path}"


@tool
def search_replace(path: str, search: str, replace: str) -> str:
    """Search and replace a specific string in a file."""
    full_path = (BASE_DIR / path).resolve()

    if not is_safe_path(full_path):
        return "Error: Access denied."

    if not full_path.exists():
        return f"Error: File '{path}' not found."

    content = full_path.read_text(encoding="utf-8")

    if search not in content:
        return f"Error: String '{search}' not found in file."

    new_content = content.replace(search, replace)
    full_path.write_text(new_content, encoding="utf-8")
    return f"Successfully updated: {path}"


@tool
def delete_file(path: str) -> str:
    """Delete a file from the workspace."""
    full_path = (BASE_DIR / path).resolve()

    if not is_safe_path(full_path):
        return "Error: Access denied."

    if not full_path.exists():
        return f"Error: File '{path}' not found."

    full_path.unlink()
    return f"Successfully deleted: {path}"


@tool
def rename_file(old_path: str, new_path: str) -> str:
    """Rename or move a file within the workspace."""
    old_full = (BASE_DIR / old_path).resolve()
    new_full = (BASE_DIR / new_path).resolve()

    if not is_safe_path(old_full) or not is_safe_path(new_full):
        return "Error: Access denied."

    if not old_full.exists():
        return f"Error: File '{old_path}' not found."

    os.makedirs(new_full.parent, exist_ok=True)
    old_full.rename(new_full)
    return f"Successfully moved '{old_path}' to '{new_path}'"


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
