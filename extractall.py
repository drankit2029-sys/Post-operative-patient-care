import os
from pathlib import Path

# Root directory of execution
ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT_DIR / "complete_project_code.txt"

# Directory names to completely skip
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".codesandbox",
    ".devcontainer",
    "dist",
    "build",
    ".next",
    ".idea",
    ".vscode",
}

# Binary, lock, and compiled file extensions to skip
IGNORED_EXTENSIONS = {
    # Database and Cache
    ".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm",
    # Compiled and Library Binaries
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib", ".exe", ".o", ".obj",
    # Images and Media
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".svg", ".mp4", ".mov", ".pdf",
    # Compressed archives
    ".zip", ".tar", ".gz", ".7z", ".rar",
    # Package lockfiles and map files
    ".lock", ".map",
}

# Source code and config extensions to explicitly capture
WHITELISTED_EXTENSIONS = {
    # Python
    ".py", ".pyi",
    # Frontend / Web
    ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss",
    # Configuration / Shell / Doc
    ".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".env.example",
    ".txt", ".md", ".sh", ".sql", "Dockerfile",
}

# Specific files to ignore
IGNORED_FILES = {
    "bundle_project.py",
    "backend_dump.txt",
    "complete_project_code.txt",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}


def bundle_repository():
    file_count = 0

    print(f"Scanning project root: {ROOT_DIR}")
    print(f"Writing destination:   {OUTPUT_FILE}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for root, dirs, files in os.walk(ROOT_DIR):
            # Prune ignored directories in-place to avoid traversing them
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for file_name in sorted(files):
                if file_name in IGNORED_FILES:
                    continue

                file_path = Path(root) / file_name
                ext = file_path.suffix.lower()

                # Filter extensions
                if ext in IGNORED_EXTENSIONS:
                    continue

                # Check if it is a relevant source/config file
                if ext not in WHITELISTED_EXTENSIONS and file_name not in WHITELISTED_EXTENSIONS:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    rel_path = file_path.relative_to(ROOT_DIR)

                    out.write(f"\n{'=' * 80}\n")
                    out.write(f"FILE: {rel_path}\n")
                    out.write(f"{'=' * 80}\n\n")
                    out.write(content)
                    out.write("\n")

                    file_count += 1
                    print(f"Included: {rel_path}")

                except (UnicodeDecodeError, PermissionError):
                    # Skip files that cannot be decoded as UTF-8
                    continue

    print(f"\nDone. Successfully compiled {file_count} files into {OUTPUT_FILE.name}")


if __name__ == "__main__":
    bundle_repository()