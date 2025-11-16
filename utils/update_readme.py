#!/usr/bin/env python3
"""
Simple README Generator - Lists all project files as links
"""

import os
from pathlib import Path

def scan_files() -> list:
    """Scan repository for all files."""
    repo_root = Path(__file__).parent.parent
    files = []

    # Directories to scan
    for directory in ['docker', 'dev', 'utils']:
        dir_path = repo_root / directory
        if dir_path.exists():
            for file in sorted(dir_path.iterdir()):
                if file.is_file():
                    files.append(f"{directory}/{file.name}")

    # Root level files
    for file in sorted(repo_root.iterdir()):
        if file.is_file() and file.suffix in ['.sh', '.md', '.py']:
            if file.name != 'README.md':  # Don't include the README itself
                files.append(file.name)

    return sorted(files)

def generate_readme(files: list) -> str:
    """Generate README with file links."""
    readme = "# Helper Scripts\n\n"

    for file in files:
        readme += f"- [{file}]({file})\n"

    return readme

def main():
    """Main function."""
    files = scan_files()
    readme_content = generate_readme(files)

    # Write README
    repo_root = Path(__file__).parent.parent
    readme_path = repo_root / 'README.md'

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print(f"README.md updated with {len(files)} files")

if __name__ == '__main__':
    main()
