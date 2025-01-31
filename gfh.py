import os
from fnmatch import fnmatch

# Project root is where this script is located
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "FIPLI_FILE_HIERARCHY.md")

# Exclude completely (hardcoded because these are always useless)
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "venv"}

# Exclude specific file types
EXCLUDE_FILES = {"*.pyc", "*.sqbpro"}

# Hide contents for these folders but still show them
HIDE_CONTENTS_FOR = {"tests"}

# Include Markdown files but exclude all other dotfiles
INCLUDE_ROOT_EXTENSIONS = {".md"}

def should_include(path, is_dir=False):
    """Decides if a file or directory should be included in the hierarchy."""
    parts = os.path.relpath(path, PROJECT_ROOT).split(os.sep)

    # Exclude unwanted directories
    if any(part in EXCLUDE_DIRS for part in parts):
        return False

    # Hide files inside specific folders (like `tests/`)
    if not is_dir and len(parts) > 1 and parts[-2] in HIDE_CONTENTS_FOR:
        return False

    # Exclude unwanted file types
    if any(fnmatch(os.path.basename(path), pattern) for pattern in EXCLUDE_FILES):
        return False

    # Exclude all dotfiles except markdown files at root level
    if os.path.basename(path).startswith("."):
        if os.path.dirname(path) == PROJECT_ROOT and os.path.splitext(path)[-1] in INCLUDE_ROOT_EXTENSIONS:
            return True  # Allow only markdown files at root
        return False  # Exclude all other dotfiles

    return True

def generate_hierarchy():
    """Scans the project and writes the filtered hierarchy to a file."""
    with open(OUTPUT_FILE, "w") as f:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            rel_root = os.path.relpath(root, PROJECT_ROOT)

            if not should_include(root, is_dir=True):
                continue

            # Write folder name with correct indentation
            indent = " " * (rel_root.count(os.sep) * 4)
            f.write(f"{indent}{os.path.basename(root)}/\n")

            if os.path.basename(root) in HIDE_CONTENTS_FOR:
                continue  # Skip listing files inside hidden-content folders

            # Write included files
            subindent = " " * ((rel_root.count(os.sep) + 1) * 4)
            for file in files:
                file_path = os.path.join(root, file)
                if should_include(file_path):
                    f.write(f"{subindent}{file}\n")

if __name__ == "__main__":
    generate_hierarchy()
