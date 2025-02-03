import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "txt_files")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

OUTPUT_FILES = {
    "backend": os.path.join(OUTPUT_DIR, "backend_combined.txt"),
    "tests": os.path.join(OUTPUT_DIR, "tests_combined.txt"),
    "docs": os.path.join(OUTPUT_DIR, "docs_combined.txt"),
    "full_project": os.path.join(OUTPUT_DIR, "full_project_code.txt"),
}

for file in OUTPUT_FILES.values():
    open(file, "w").close()  # Wipes content if file exists, creates if not

backend_files, tests_files, docs_files = [], [], []

GLOBAL_EXCLUDED_DIRS = {"venv", "__pycache__", ".pytest_cache__", ".cursor", "CURSOR_JOURNAL", "IGNORE"}

def format_file_content(filepath):
    relative_path = os.path.relpath(filepath, PROJECT_ROOT).replace("\\", "/")
    with open(filepath, "r", encoding="utf-8") as f:
        content = "\n".join(line for line in f.read().splitlines() if line.strip())
    return f"######## {relative_path} ########\n```\n{content}\n```\n\n"

for root, dirs, files in os.walk(PROJECT_ROOT):
    rel_root = os.path.relpath(root, PROJECT_ROOT).replace("\\", "/")
    root_folder = os.path.basename(root)

    if any(excluded in rel_root.split("/") for excluded in GLOBAL_EXCLUDED_DIRS):
        continue

    if root_folder == "docs":
        for file in files:
            if file.endswith((".md", ".txt")):
                docs_files.append(os.path.join(root, file))

    if root_folder == "tests":
        for file in files:
            if file.endswith(".py"):
                tests_files.append(os.path.join(root, file))

    if "docs" not in rel_root.split("/") and "tests" not in rel_root.split("/"):
        for file in files:
            if file.endswith(".py"):
                backend_files.append(os.path.join(root, file))

for category, file_list in [("backend", backend_files), ("tests", tests_files), ("docs", docs_files)]:
    with open(OUTPUT_FILES[category], "w", encoding="utf-8") as output_file:
        for file in file_list:
            output_file.write(format_file_content(file))

with open(OUTPUT_FILES["full_project"], "w", encoding="utf-8") as full_project:
    for category in ["docs", "backend", "tests"]:
        with open(OUTPUT_FILES[category], "r", encoding="utf-8") as partial_file:
            full_project.write(partial_file.read())
